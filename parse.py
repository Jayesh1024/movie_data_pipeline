from selenium import webdriver
from bs4 import BeautifulSoup
import re
import random
import json
from datetime import datetime


def XPathToSelector(xpath):
    '''
    Converts a given xpath to a css selector path

    :param xpath: The required XPath
    :type xpath: str

    :rtype: str
    :returns: The CSS Selector for the input XPath
    '''
    
    pattern=r'//\*\[@id="(.*)"](.*)'
    matches=re.findall(pattern=pattern,string=xpath)
    id=matches[0][0]
    path=matches[0][1].replace('/','>')
    path_matches=re.finditer(pattern=r'\[(\d+)\]',string=path)
    for match in path_matches:
        replacement=match.group(1)
        path=re.sub(pattern=r'\[\d+\]',repl=f":nth-of-type({replacement})",string=path,count=1)
    selector="#"+id+path
    return selector


def fact_parser(collection_fp):

    with open(collection_fp,'r') as f:
        soup=BeautifulSoup(f,features='html.parser')

    movie_rows=soup.select("#table > div > table.a-bordered.a-horizontal-stripes.a-size-base.a-span12.mojo-body-table.mojo-table-annotated.mojo-body-table-compact.scrolling-data-table > tbody > tr:nth-child(n)")
    movie_fact_table=[]
    for i,row in enumerate(movie_rows):
        row_dict={}
        
        date_text=soup.select_one("#a-page > main > div > div > h1").text
        date_pattern=r'\w*\s+\d,\s+\d{4}'
        movie_collection_date_str=re.findall(pattern=date_pattern,string=date_text)[0]
        date_id=str(datetime.strptime(movie_collection_date_str,"%b %d, %Y").date()).replace('-','')
        row_dict['date_id']=date_id
        row_dict['updated_at_id']=str(datetime.today().date()).replace('-','')
        row_dict['num_of_releases']=len(movie_rows)
        if i>0 :
            cells=row.find_all('td')
            
            for j,cell in enumerate(cells):
                if j==0:
                    row_dict['rank']=cell.text
                elif j==2:
                    movie_page_link="https://boxofficemojo.com"+cell.find('a').attrs['href']
                    driver=webdriver.Chrome()
                    driver.get(movie_page_link)
                    soup_movie=BeautifulSoup(driver.page_source,features='html.parser')
                    movie_id=soup_movie.select_one("#title-summary-refiner > a").attrs['href'].split('/')[-2]
                    row_dict['movie_id']=movie_id
                    row_dict['movie_name']=cell.text
                elif j==3:
                    row_dict['collection_domestic']=cell.text
                elif j==6:
                    row_dict['num_theatres']=cell.text
                elif j==9:
                    row_dict['days_post_release']=cell.text
                

            
            movie_fact_table.append(row_dict)

    return movie_fact_table


def movie_parser(movie_fp,movie_fp_imdb):
    '''
    Parses the movie html page and returns a python dict object
    which have the desired dimension attributes.

    :type movie_file_fp: str
    :param movie_file_fp: Path of the movie html page

    :rtype: dict
    :returns: Python dictionary with movie dimension attributes
    '''

    with open(movie_fp,'r') as f:
        movie_soup = BeautifulSoup(f,features='html.parser')
    with open(movie_fp_imdb,'r') as f:
        movie_soup_imdb = BeautifulSoup(f,features='html.parser')

    movie_data_dict={}
    movie_data_dict['movie_name']=movie_soup.select_one("#a-page > main > div > div.a-section.a-spacing-none.mojo-summary > div.a-section.mojo-heading-summary > div > div > div.a-fixed-left-grid-col.a-col-right > h1").text
    movie_data_dict['movie_id']=movie_soup.select_one("#title-summary-refiner > a").get('href').split('/')[-2]
    movie_release_data_rows=movie_soup.select("#a-page > main > div > div.a-section.a-spacing-none.mojo-gutter.mojo-summary-table > div.a-section.a-spacing-none.mojo-summary-values.mojo-hidden-from-mobile > div:nth-child(n)")
    
    for row in movie_release_data_rows:
        child_span=[child for child in row.children]
        if 'Distributor' in child_span[0].text:
            movie_data_dict['distributor_id']=child_span[1].find('a').attrs['href'].split('/')[-3]
        elif 'Release Date' in child_span[0].text:
            movie_data_dict['release_date_id']=str(datetime.strptime(child_span[1].text,"%d-%b-%Y").date()).replace('-','')
        elif 'MPAA' in child_span[0].text:
            movie_data_dict['rating']=child_span[1].text
        elif 'Running Time' in child_span[0].text:
            running_time=child_span[1].text
            running_time_pattern=r'(\d)\s*hr\s*(\d*)\s*min'
            re_match=re.findall(pattern=running_time_pattern,string=running_time)
            movie_data_dict['duration']=int(re_match[0][0])*60+int(re_match[0][1])
        
        elif 'Widest Release' in child_span[0].text:
            movie_data_dict['widest_release']=child_span[1].text.split(' ')[0].replace(',','')

    imdb_rating_num_of_ratings=movie_soup_imdb.select_one("#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-afa4bed1-0.iMxoKo > section > div:nth-child(5) > section > section > div:nth-child(2) > div:nth-child(2) > div > div:nth-child(1) > a").text.split('/')
    movie_data_dict['imdb_rating']=imdb_rating_num_of_ratings[0]
    movie_data_dict['num_of_rating']=imdb_rating_num_of_ratings[1][2:]
    if 'K' in movie_data_dict['num_of_rating']:
        movie_data_dict['num_of_rating']=int(float(movie_data_dict['num_of_rating'][:-1])*1000)
    elif 'M' in movie_data_dict['num_of_rating']:
        movie_data_dict['num_of_rating']=int(float(movie_data_dict['num_of_rating'][:-1])*1000000)

    return movie_data_dict   

def genre_parser(page_fp_num_of_rating,page_fp_us_box_office):
    '''
    Parses the genre dimension attributes from html to a python dict object
    
    :type page_fp_num_of_rating: str
    :type page_fp_us_box_office: str
    :param page_fp_num_of_rating: genre page file path for the page sorted by number of ratings
    :param page_fp_us_box_office: genre page file path for the page sorted by us box office collection
    
    :rtype: dict
    :returns: A python dict which represents the genre dimension attributes
    '''
    with open(page_fp_num_of_rating,'r') as f:
        soup_num_of_rating=BeautifulSoup(f,features='html.parser')
    with open(page_fp_us_box_office,'r') as f:
        soup_us_box_office=BeautifulSoup(f,features='html.parser')
    
    genre_dict={}
    genre_dict['genre_id']=page_fp_num_of_rating.split('/')[1].split('_')[0]
    genre_dict['genre_name']=soup_num_of_rating.select_one("#__next > main > div:nth-of-type(2) > div:nth-of-type(3) > section > section > div > section > section > div:nth-child(2) > div > section > div:nth-of-type(1) > div > div > div.ipc-chip-list__scroller > button:nth-child(2)").text
    genre_dict['total_movies']=soup_num_of_rating.select_one("#__next > main > div:nth-of-type(2) > div:nth-of-type(3) > section > section > div > section > section > div:nth-child(2) > div > section > div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(1) > div:nth-of-type(1)").text.split(' ')[-1].replace(',','') 
    genre_dict['top_movie_NumOfRating']=soup_num_of_rating.select_one("#__next > main > div:nth-of-type(2) > div:nth-of-type(3) > section > section > div > section > section > div:nth-child(2) > div > section > div:nth-of-type(2) > div:nth-of-type(2) > ul > li:nth-child(1) > div > div > div > div:nth-of-type(1) > div:nth-of-type(1) > div > a").get('href').split('/')[-2]
    genre_dict['top_movie_US_BoxOffice']=soup_us_box_office.select_one("#__next > main > div:nth-of-type(2) > div:nth-of-type(3) > section > section > div > section > section > div:nth-child(2) > div > section > div:nth-of-type(2) > div:nth-of-type(2) > ul > li:nth-child(1) > div > div > div > div:nth-of-type(1) > div:nth-of-type(1) > div > a").get('href').split('/')[-2]


def filmmaker_parser(filmmaker_profile_fp,filmmaker_num_of_rating_fp,filmmaker_us_box_office_fp,filmmaker_debut_movie_fp):
    with open(filmmaker_profile_fp,'r') as f:
        soup_profile=BeautifulSoup(f,features='html.parser')

    with open(filmmaker_num_of_rating_fp,'r') as f:
        soup_num_of_rating=BeautifulSoup(f,features='html.parser')

    with open(filmmaker_us_box_office_fp,'r') as f:
        soup_us_box_office=BeautifulSoup(f,features='html.parser')

    with open(filmmaker_debut_movie_fp,'r') as f:
        soup_debut_movie=BeautifulSoup(f,features='html.parser')
    

    filmmaker_dict={}
    filmmaker_dict['filmmaker_id']=filmmaker_profile_fp.split('/')[-1].split('_')[-1].split('.')[0]
    filmmaker_dict['name']=soup_profile.select_one(XPathToSelector('''//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div/h1/span[1]''')).text
    filmmaker_birth_details=soup_profile.find('li',attrs={'data-testid':'nm_pd_bl'}).select("div>ul>li")
    dob=filmmaker_birth_details[0].text
    filmmaker_dict['dob']=datetime.strptime(dob,"%B %d, %Y").date()
    location=filmmaker_birth_details[1].text
    filmmaker_dict['place_of_birth']=location
    location=location.split(',')
    filmmaker_dict['country']=location[-1]
    filmmaker_dict['total_movies']=soup_num_of_rating.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/div[1]/div[1]''')).text.split(' ')[-1]
    filmmaker_dict['top_movie_NumOfRating']=soup_num_of_rating.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[1]/div/div/div/div[1]/div[2]/div[1]/a''')).get('href').split('/')[-2]
    filmmaker_dict['top_movie_US_BoxOffice']=soup_us_box_office.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[1]/div/div/div/div[1]/div[2]/div[1]/a''')).get('href').split('/')[-2]
    filmmaker_dict['debut_movie_id']= soup_debut_movie.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[1]/div/div/div/div[1]/div[2]/div[1]/a''')).get('href').split('/')[-2]
    
    return filmmaker_dict


def distributor_parser(dist_num_of_ratings_fp,dist_us_box_office_fp):
    with open(dist_num_of_ratings_fp,'r') as f:
        soup_num_of_rating=BeautifulSoup(f,features='html.parser')
    with open(dist_us_box_office_fp,'r') as f:
        soup_us_box_office=BeautifulSoup(f,features='html.parser')
    distributor_dict={}
    distributor_dict['distributor_id']=dist_num_of_ratings_fp.split('/')[-1].split('_')[0]
    distributor_dict['distributor_name']=soup_num_of_rating.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[1]/div/div/div[2]/button[2]''')).text
    distributor_dict['total_movies']=soup_num_of_rating.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/div[1]/div[1]''')).text.split(' ')[-1]
    distributor_dict['top_movie_NumOfRating']=soup_num_of_rating.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[1]/div/div/div/div[1]/div[2]/div[1]/a''')).get('href').split('/')[-2]
    distributor_dict['top_movie_US_BoxOffice']=soup_us_box_office.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[1]/div/div/div/div[1]/div[2]/div[1]/a''')).get('href').split('/')[-2]
    return distributor_dict

