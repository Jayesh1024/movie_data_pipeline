from selenium import webdriver
import time
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
import pytz
import json
ist_tz=pytz.timezone('Asia/Kolkata')
driver=webdriver.Chrome()
def page_extract(date):
    '''
    Saves the daily box office collection page of boxofficemojo.com to daily_box_office/ for input date

    :type date: str
    :param date: date for which to save the box office collection html page
    '''
    link=f"https://www.boxofficemojo.com/date/{date}/"
    driver.get(link)
    html_page=driver.page_source
    boxoffice_collection_daily={
        'url':link,
        'extracted_at':str(datetime.now()),
        'collection_date':date,
        'page_source':html_page
    }
    path=f'daily_box_office/boxoffice_{str(date).replace('-','')}.json'
    with open(path,'w') as f:
        json.dump(obj=boxoffice_collection_daily,fp=f,indent=2)
    return path
    
    
def movie_page_extract(collection_parsed_fp): 
    '''
    Saves the html page for every movie in the given box office collection html page file path to movie_pages/

    :type collection_page_fp: str
    :param collection_page_fp: file path of the box office collection html page
    
    '''
    movies_parsed=[]
    
    with open(collection_parsed_fp,'r') as f:
        collection_html_source:list[dict]
        collection_html_source=json.load(f)
    
    for movie_html in collection_html_source[:5]:
        
        movie_individual_dict={
        'extracted_at':str,
        'run_date':str,
        'content':{
            'movie_id':str,
            'release_id':str,
            'url_boxofficemojo':str,
            'url_imdb':str,
            'page_source':{
                'boxofficemojo':str,
                'imdb':str
            }
        }
        }

        movie_individual_dict['run_date']=movie_html['run_date']
        movie_individual_dict['content']['release_id']=movie_html['release_id']
        movie_individual_dict['content']['url_boxofficemojo']=f'https://boxofficemojo.com/release/{movie_html['release_id']}/'
        movie_individual_dict['extracted_at']=str(datetime.now(tz=ist_tz))
        driver.get(movie_individual_dict['content']['url_boxofficemojo'])
        movie_individual_dict['content']['page_source']['boxofficemojo']=driver.page_source
        movie_soup=BeautifulSoup(movie_individual_dict['content']['page_source']['boxofficemojo'],features='html.parser')
        movie_link_imdb="https://imdb.com"+movie_soup.select_one("#title-summary-refiner > a").attrs['href']
        movie_individual_dict['content']['movie_id']=movie_link_imdb.split('/')[-2]
        movie_individual_dict['content']['url_imdb']=movie_link_imdb
        driver.get(movie_link_imdb)
        movie_individual_dict['content']['page_source']['imdb']=driver.page_source
        movies_parsed.append(movie_individual_dict)
    
    path=f'movies_html_source_{collection_html_source[0]['run_date']}.json'
    with open(path,'w') as f:
        json.dump(obj=movies_parsed,fp=f,indent=2)
    return path

def movie_cast_filmmakers_extract(parsed_movie_json_fp): # Takes the file path to individual movie and extracts and save the cast and crew info page from imdb.com to cast_pages directory
    with open(parsed_movie_json_fp,'r') as f:
        movies_parsed=json.load(f)

    # Definition of response which will be saved by this function
    # response={
    #     'extracted_at':str,
    #     'run_date':str,
    #     'content':[
    #         {
    #             'movie_id':str,
    #             'filmmaker_id':str,
    #             'role':str,
    #             'page_source':{
    #                 'profile':{
    #                     'url':str,
    #                     'source':str
    #                 },
    #                 'search_num_of_ratings':{
    #                     'url':str,
    #                     'source':str
    #                 },
    #                 'search_us_box_office':{
    #                     'url':str,
    #                     'source':str
    #                 },
    #                 'search_debut_movie':{
    #                     'url':str,
    #                     'source':str
    #                 }
    #             }
    #         }
    #     ]
    # }
    response:dict={}

    response['extracted_at']=movies_parsed['extracted_at']
    response['run_date']=movies_parsed['run_date']
    response['content']=[]

    for movie in movies_parsed['content']:
        for filmmaker in movie['filmmakers']:
            id=filmmaker['filmmaker_id']
            filmmaker_dict={
                'movie_id':movie['movie_id'],
                'filmmaker_id':id,
                'role':filmmaker['role'],
                'page_source':{
                    'profile':{},
                    'search_num_of_ratings':{},
                    'search_us_box_office':{},
                    'search_debut_movie':{}
                }
            }
            links={
            "profile":f"https://www.imdb.com/name/{id}/",
            "search_num_of_ratings":f"https://www.imdb.com/search/title/?title_type=feature&role={id}&sort=num_votes,desc",
            "search_us_box_office":f"https://www.imdb.com/search/title/?title_type=feature&role={id}&sort=boxoffice_gross_us,desc",
            "search_debut_movie":f"https://www.imdb.com/search/title/?title_type=feature&role={id}&sort=release_date,asc"
            }
            
            for type,link in links.items():
                driver.get(link)
                filmmaker_dict['page_source'][type]['url']=link
                filmmaker_dict['page_source'][type]['source']=driver.page_source
            
            response['content'].append(filmmaker_dict)


    path=f"filmmaker_html_{movies_parsed['run_date']}.json"
    with open(path,'w') as f:
        json.dump(response,f,indent=2)

    return path
            
    
def genre_scraper(parsed_movie_json_fp):
    '''
    Saves the genre page html file by number of ratings and us box office collection.\n
    For every genre page there are two sorting types\n
    1. Number of rating sorting types are stored in genre_pages_num_of_rating/\n
    2. US box office collection sorting types are stored in genre_pages_us_box_office/


    :type: str
    :param movie_page_fp: movie page html file path (located in movie_pages/)
    
    '''
    with open(parsed_movie_json_fp,'r') as f:
        movies_parsed=json.load(f)


    # This is the definition of the saved response of this function
    # response={
    #     "extracted_at":str,
    #     "run_date":str,
    #     "content":[                   # This key can have multiple elements each representing a genre
    #         {
    #             "movie_id":str,       # movie_id this genre is associated with
    #             "genre_id":str,       # genre_id of the genre being scraped
    #             "page_source":{
    #                 "num_of_ratings":{
    #                     "url":str,
    #                     "source":str
    #                 },
    #                 "us_box_office_collection":{
    #                     "url":str,
    #                     "source":str
    #                 }
    #             }
    #         }
    #     ]
    # }
    
    response={
        "extracted_at":movies_parsed['extracted_at'],
        "run_date":movies_parsed['run_date'],
        "content":[]
    }

    for movie in movies_parsed['content']:
        for genre_id in movie['genres']:
            genre={}
            genre_link_num_of_rating_sorted=f"https://www.imdb.com/search/title/?title_type=feature&interests={genre_id}&sort=num_votes,desc"
            driver.get(genre_link_num_of_rating_sorted)
            genre_page_ratings=driver.page_source

            genre_link_us_box_office_collection_sorted=f"https://www.imdb.com/search/title/?title_type=feature&interests={genre_id}&sort=boxoffice_gross_us,desc"
            driver.get(genre_link_us_box_office_collection_sorted)
            genre_page_boxoffice=driver.page_source
            
            genre['movie_id']=movie['movie_id']
            genre['genre_id']=genre_id
            genre['page_source']={}
            genre['page_source']['num_of_ratings']={
                'url':genre_link_num_of_rating_sorted,
                'source':genre_page_ratings
            }
            genre['page_source']['us_box_office_collection']={
                'url':genre_link_us_box_office_collection_sorted,
                'source':genre_page_boxoffice
            }
            response['content'].append(genre)
    
    path=f"genre_html_{response['run_date']}.json"
    with open(path,'w') as f:
        json.dump(response,f,indent=2)
    
    return path



            

def distributor_scraper(movie_parsed_fp):
    '''
    Saves the distributor html page for following sort types to get top movies by\n
    1. Number of ratings\n Saves to distributor_pages_num_of_rating/\n
    2. US box office collection\n Saves to distributor_pages_us_box_office/

    :type movie_page_fp: str
    :param movie_page_fp: movie page file path of box office mojo site

    '''
    with open(movie_parsed_fp,'r') as f:
        movies_parsed=json.load(f)
    
    # response={
    #     "extracted_at":str,
    #     "run_date":str,
    #     "content":[                   # This key can have multiple elements each representing a genre
    #         {
    #             "movie_id":str,       # movie_id this genre is associated with
    #             "distributor_id":str,       # genre_id of the genre being scraped
    #             "page_source":{
    #                 "num_of_ratings":{
    #                     "url":str,
    #                     "source":str
    #                 },
    #                 "us_box_office_collection":{
    #                     "url":str,
    #                     "source":str
    #                 }
    #             }
    #         }
    #     ]
    # }

    response={
        'extracted_at':movies_parsed['extracted_at'],
        'run_date':movies_parsed['run_date'],
        'content':[]
    }

    for movie in movies_parsed['content']:

        distributor_dict={}
        distributor_id=movie['distributor_id']
        distributor_dict['movie_id']=movie['movie_id']
        distributor_dict['distributor_id']=distributor_id

        distributor_link_num_of_ratings=f"https://www.imdb.com/search/title/?title_type=feature&companies={distributor_id}&sort=num_votes,desc"
        driver.get(distributor_link_num_of_ratings)
        page_rating=driver.page_source

        distributor_link_us_box_office=f"https://www.imdb.com/search/title/?title_type=feature&companies={distributor_id}&sort=boxoffice_gross_us,desc"
        driver.get(distributor_link_us_box_office)
        page_collection=driver.page_source

        distributor_dict['page_source']={
            "num_of_ratings":{
                "url":distributor_link_num_of_ratings,
                "source":page_rating
            },
            "us_box_office_collection":{
                "url":distributor_link_us_box_office,
                "source":page_collection
            }
        }

        response['content'].append(distributor_dict)
    
    path=f"distributor_html_{movies_parsed['run_date']}.json"
    with open(path,'w') as f:
        json.dump(response,f,indent=2)
    
    return path



