from selenium import webdriver
from bs4 import BeautifulSoup
import re
import random
import json
from datetime import datetime
driver=webdriver.Chrome()

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


movie_parser("movie_pages/tt11315808.html","movie_pages/tt11315808_imdb.html")    