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


def fact_parser(collection_json_path):
    with open(collection_json_path,'r') as f:
        collection_json=json.load(fp=f)

    soup=BeautifulSoup(collection_json['page_source'],features='html.parser')

    movie_rows=soup.select("#table > div > table.a-bordered.a-horizontal-stripes.a-size-base.a-span12.mojo-body-table.mojo-table-annotated.mojo-body-table-compact.scrolling-data-table > tbody > tr:nth-child(n)")
    movie_fact_table:list[dict]
    movie_fact_table=[]
    for i,row in enumerate(movie_rows):

        row_dict={
            'run_date':str,
            'updated_at_id':str,
            'num_of_releases':int,
            'rank':str,
            'release_id':str,
            'movie_name':str,
            'collection_domestic':str,
            'num_theatres':str,
            'days_post_release':str
        }
        
        row_dict['run_date']=collection_json['collection_date'].replace('-','')
        row_dict['updated_at_id']=str(datetime.today().date()).replace('-','')
        row_dict['num_of_releases']=len(movie_rows)-1
        if i>0 :
            cells=row.find_all('td')
            
            for j,cell in enumerate(cells):
                if j==0:
                    row_dict['rank']=cell.text
                elif j==2:
                    movie_page_link="https://boxofficemojo.com"+cell.find('a').attrs['href']
                    row_dict['release_id']=movie_page_link.split('/')[-2]
                    row_dict['movie_name']=cell.text
                elif j==3:
                    row_dict['collection_domestic']=cell.text
                elif j==6:
                    row_dict['num_theatres']=cell.text
                elif j==9:
                    row_dict['days_post_release']=cell.text
                

            
            movie_fact_table.append(row_dict)
    path=f'daily_box_office/collection_parsed_{collection_json['collection_date'].replace('-','')}.json'
    with open(path,'w') as f:
        json.dump(obj=movie_fact_table,fp=f,indent=2)
    return path

#TODO: change how this func takes inputs (which is in form of josn) and then processes it
def movie_parser(movies_json_fp):
    '''
    Parses the movie html page and returns a python dict object
    which have the desired dimension attributes.

    :type movie_file_fp: str
    :param movie_file_fp: Path of the movie html page

    :rtype: dict
    :returns: Python dictionary with movie dimension attributes
    '''

    with open(movies_json_fp,'r') as f:
        movies_json=json.load(f)
    
    movies=[]

    for i,movie in enumerate(movies_json[:5]):
        
        print(f'movie num : {i} getting parsed')
        movie_soup=BeautifulSoup(movie['content']['page_source']['boxofficemojo'],features='html.parser')
        movie_soup_imdb=BeautifulSoup(movie['content']['page_source']['imdb'],features='html.parser')
        
        # The definition of movies dict which will hold the movie data and will be saved

        # movies={
        #     "extracted_at":str,
        #     "run_date":str,
        #     "content":[                               # "content" included individual movie data wrapped in a list
        #         {                                     # We also call this movie data as movie data dict below in the code, so content holds multiple movie_data_dict
        #             'movie_id':str,                   
        #             'movie_name':str,
        #             'release_date_id':str,
        #             'rating':str,
        #             'distributor_id':str,
        #             'duration':int,
        #             'widest_release':str,
        #             'imdb_rating':str,
        #             'num_of_rating':int,
        #             'genres':list,                    # This consist of the multiple genres which the movie_id
        #             'filmmakers':[                    # This consist of the filmmakers data wrapped in a list which are associated with the movie_id
        #                 {
        #                     "filmmaker_id":str,
        #                     "role":str
        #                 }
        #             ]
        #         }
        #     ]
        # }
        movie_data_dict={}
        movie_data_dict['movie_name']=movie_soup.select_one("#a-page > main > div > div.a-section.a-spacing-none.mojo-summary > div.a-section.mojo-heading-summary > div > div > div.a-fixed-left-grid-col.a-col-right > h1").text
        movie_data_dict['movie_id']=movie_soup.select_one("#title-summary-refiner > a").get('href').split('/')[-2]
        movie_release_data_rows=movie_soup.select("#a-page > main > div > div.a-section.a-spacing-none.mojo-gutter.mojo-summary-table > div.a-section.a-spacing-none.mojo-summary-values.mojo-hidden-from-mobile > div:nth-child(n)")
        
        for row in movie_release_data_rows:
            child_span=[child for child in row.children]
            if 'Distributor' in child_span[0].text:
                movie_data_dict['distributor_id']=child_span[1].find('a').attrs['href'].split('/')[-3]
            elif 'Release Date' in child_span[0].text:
                release_date=child_span[1].text
                if len(release_date.split(' '))==2:
                    release_date=release_date.split(' ')[0]
                movie_data_dict['release_date_id']=str(datetime.strptime(release_date,"%d-%b-%Y").date()).replace('-','')
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
        
        genre_anchors=movie_soup_imdb.select_one(XPathToSelector('''//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]''')).find_all('a')
        movie_data_dict['genres']=[anchor.get('href').split('/')[-2] for anchor in genre_anchors]
        
        directors=[{"filmmaker_id":anchor.get('href').split('/')[-2],"role":"director"} for anchor in movie_soup_imdb.select_one(XPathToSelector('''//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/div[2]/div/ul/li[1]/div/ul''')).find_all('a')]
        writers=[{"filmmaker_id":anchor.get('href').split('/')[-2],"role":"writer"} for anchor in movie_soup_imdb.select_one(XPathToSelector('''//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/div[2]/div/ul/li[2]/div/ul''')).find_all('a')]
        stars=[{"filmmaker_id":anchor.get('href').split('/')[-2],"role":"star"} for anchor in movie_soup_imdb.select_one(XPathToSelector('''//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/div[2]/div/ul/li[3]/div/ul''')).find_all('a')]
        movie_data_dict['filmmakers']=[]
        movie_data_dict['filmmakers'].extend(directors)
        movie_data_dict['filmmakers'].extend(writers)
        movie_data_dict['filmmakers'].extend(stars)
        movies.append(movie_data_dict)
    
    movies={
        "extracted_at":movies_json[0]['extracted_at'],
        "run_date":movies_json[0]['run_date'],
        "content":movies
    }
    path=f'movies_parsed_{movies_json[0]['run_date']}.json'
    with open(path,'w') as f:
        json.dump(obj=movies,fp=f,indent=2)
    return path

def genre_parser(genre_html_json_fp):
    '''
    Parses the genre dimension attributes from html to a python dict object
    
    :type page_fp_num_of_rating: str
    :type page_fp_us_box_office: str
    :param page_fp_num_of_rating: genre page file path for the page sorted by number of ratings
    :param page_fp_us_box_office: genre page file path for the page sorted by us box office collection
    
    :rtype: dict
    :returns: A python dict which represents the genre dimension attributes
    '''
    with open(genre_html_json_fp,'r') as f:
        genre_html=json.load(f)
    
    # Definition of the genre response this function will save
    # response={
    #     "extracted_at":str,
    #     "run_date":str,
    #     "content":[
    #         {
    #             "movie_id":str,
    #             "genre_id":str,
    #             "genre_name":str,
    #             "total_movies":str,
    #             "top_movie_NumOfRating":str,
    #             "top_movie_US_BoxOffice":str

    #         }
    #     ]
    # }

    response:dict={}
    response['extracted_at']=genre_html['extracted_at']
    response['run_date']=genre_html['run_date']
    response['content']=[]



    for genre in genre_html['content']:
        genre_dict={}
        genre_dict['movie_id']=genre['movie_id']
        genre_dict['genre_id']=genre['genre_id']
        soup_num_of_rating=BeautifulSoup(genre['page_source']['num_of_ratings']['source'],features='html.parser')
        soup_us_box_office=BeautifulSoup(genre['page_source']['us_box_office_collection']['source'],features='html.parser')
        genre_dict['genre_name']=soup_num_of_rating.select_one("#__next > main > div:nth-of-type(2) > div:nth-of-type(3) > section > section > div > section > section > div:nth-child(2) > div > section > div:nth-of-type(1) > div > div > div.ipc-chip-list__scroller > button:nth-child(2)").text
        genre_dict['total_movies']=soup_num_of_rating.select_one("#__next > main > div:nth-of-type(2) > div:nth-of-type(3) > section > section > div > section > section > div:nth-child(2) > div > section > div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(1) > div:nth-of-type(1)").text.split(' ')[-1].replace(',','') 
        genre_dict['top_movie_NumOfRating']=soup_num_of_rating.select_one("#__next > main > div:nth-of-type(2) > div:nth-of-type(3) > section > section > div > section > section > div:nth-child(2) > div > section > div:nth-of-type(2) > div:nth-of-type(2) > ul > li:nth-child(1) > div > div > div > div:nth-of-type(1) > div:nth-of-type(1) > div > a").get('href').split('/')[-2]
        genre_dict['top_movie_US_BoxOffice']=soup_us_box_office.select_one("#__next > main > div:nth-of-type(2) > div:nth-of-type(3) > section > section > div > section > section > div:nth-child(2) > div > section > div:nth-of-type(2) > div:nth-of-type(2) > ul > li:nth-child(1) > div > div > div > div:nth-of-type(1) > div:nth-of-type(1) > div > a").get('href').split('/')[-2]
        response['content'].append(genre_dict)
    
    path=f'genre_parsed_{genre_html['run_date']}.json'
    with open(path,'w') as f:
        json.dump(response,f,indent=2)
    
    return path

def filmmaker_parser(filmmaker_html_fp):
    
    with open(filmmaker_html_fp,'r') as f:
        filmmaker_data=json.load(f)
    
    # Definition of the response which will be saved by this function
    # response={
    #     'extracted_at':str,
    #     'run_date':str,
    #     'content':[
    #         {
    #             'movie_id':str,
    #             'filmmaker_id':str,
    #             'name':str,
    #             'dob':str,
    #             'place_of_birth':str,
    #             'country':str,
    #             'total_movies':str,
    #             'top_movie_NumOfRating':str,
    #             'top_movie_US_BoxOffice':str,
    #             'debut_movie_id':str
    #         }
    #     ]
    # }

    response={
        'extracted_at':filmmaker_data['extracted_at'],
        'run_date':filmmaker_data['run_date'],
        'content':[]
    }

    for filmmaker in filmmaker_data['content']:

        filmmaker_dict={}
        filmmaker_dict['movie_id']=filmmaker['movie_id']
        filmmaker_dict['filmmaker_id']=filmmaker['filmmaker_id']

        soup_profile=BeautifulSoup(filmmaker['page_source']['profile']['source'],features='html.parser')
        soup_num_of_rating=BeautifulSoup(filmmaker['page_source']['search_num_of_ratings']['source'],features='html.parser')
        soup_us_box_office=BeautifulSoup(filmmaker['page_source']['search_us_box_office']['source'],features='html.parser')
        soup_debut_movie=BeautifulSoup(filmmaker['page_source']['search_debut_movie']['source'],features='html.parser')

        filmmaker_dict['name']=soup_profile.select_one(XPathToSelector('''//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div/h1/span[1]''')).text

        try:
            filmmaker_birth_details=soup_profile.find('li',attrs={'data-testid':'nm_pd_bl'}).select("div>ul>li")
            dob=filmmaker_birth_details[0].text
            try:
                filmmaker_dict['dob']=str(datetime.strptime(dob,"%B %d, %Y").date())
            except ValueError as e:
                filmmaker_dict['dob']=None
            location=filmmaker_birth_details[1].text
            filmmaker_dict['place_of_birth']=location
            location=location.split(',')
            filmmaker_dict['country']=location[-1]
        except AttributeError as e:
            err={
                'error_type':e,
                'mssg':'Birth details not available for the filmmaker in imdb page',
            }
            print(err)
            filmmaker_dict['dob']=None
            filmmaker_dict['place_of_birth']=None
            filmmaker_dict['country']=None
        
        try:
            filmmaker_dict['total_movies']=soup_num_of_rating.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/div[1]/div[1]''')).text.split(' ')[-1]
        except AttributeError as e:
            filmmaker_dict['total_movies']=None


        try:
            filmmaker_dict['top_movie_NumOfRating']=soup_num_of_rating.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[1]/div/div/div/div[1]/div[2]/div[1]/a''')).get('href').split('/')[-2]
        except AttributeError as e:
            filmmaker_dict['top_movie_NumOfRating']=None


        try:
            filmmaker_dict['top_movie_US_BoxOffice']=soup_us_box_office.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[1]/div/div/div/div[1]/div[2]/div[1]/a''')).get('href').split('/')[-2]
        except AttributeError as e:
            filmmaker_dict['top_movie_US_BoxOffice']=None


        try:
            filmmaker_dict['debut_movie_id']= soup_debut_movie.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[1]/div/div/div/div[1]/div[2]/div[1]/a''')).get('href').split('/')[-2]
        except AttributeError as e:
            filmmaker_dict['debut_movie_id']=None

        response['content'].append(filmmaker_dict)

    path=f'filmmaker_parsed_{filmmaker_data['run_date']}.json'
    with open(path,'w') as f:
        json.dump(response,fp=f,indent=2)

    return path


def distributor_parser(distributor_html_json_fp):
    with open(distributor_html_json_fp,'r') as f:
        distributors=json.load(f)

    # response={
    #     'extracted_at':str,
    #     'run_date':str,
    #     'content':[
    #         {
    #             'movie_id':str,
    #             'distributor_id':str,
    #             'distributor_name':str,
    #             'total_movies':str,
    #             'top_movie_NumOfRating':str,
    #             'top_movie_US_BoxOffice':str,
    #         }
    #     ]
    # }

    response={
        'extracted_at':distributors['extracted_at'],
        'run_date':distributors['run_date'],
        'content':[]
    }
    for distributor in distributors['content']:
        distributor_dict={}
        soup_num_of_rating=BeautifulSoup(distributor['page_source']['num_of_ratings']['source'],features='html.parser')
        soup_us_box_office=BeautifulSoup(distributor['page_source']['us_box_office_collection']['source'],features='html.parser')
        distributor_dict['movie_id']=distributor['movie_id']
        distributor_dict['distributor_id']=distributor['distributor_id']
        distributor_dict['distributor_name']=soup_num_of_rating.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[1]/div/div/div[2]/button[2]''')).text
        distributor_dict['total_movies']=soup_num_of_rating.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/div[1]/div[1]''')).text.split(' ')[-1]
        distributor_dict['top_movie_NumOfRating']=soup_num_of_rating.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[1]/div/div/div/div[1]/div[2]/div[1]/a''')).get('href').split('/')[-2]
        distributor_dict['top_movie_US_BoxOffice']=soup_us_box_office.select_one(XPathToSelector('''//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[1]/div/div/div/div[1]/div[2]/div[1]/a''')).get('href').split('/')[-2]
        
        response['content'].append(distributor_dict)
    
    path=f"distributor_parsed_{distributors['run_date']}.json"
    with open(path,'w') as f:
        json.dump(response,f,indent=2)

    return path

