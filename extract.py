from selenium import webdriver
from selenium.webdriver import ChromeService
from datetime import datetime
from bs4 import BeautifulSoup
import pytz
import json
from log import logger

ist_tz=pytz.timezone('Asia/Kolkata')
service=ChromeService(executable_path='./chromedriver')
driver=webdriver.Chrome(service=service)

def page_extract(date):
    try:
        link=f"https://www.boxofficemojo.com/date/{date}/"
        driver.get(link)
        html_page=driver.page_source
        boxoffice_collection_daily={
            'url':link,
            'extracted_at':str(datetime.now()),
            'collection_date':date,
            'page_source':html_page
        }
    except Exception as e:
        logger.error(f"Failed collection page extraction for run date: {date}")
        logger.exception(e)
    finally:
        path=f'run_{date.replace('-','')}/boxoffice_html_{str(date).replace('-','')}.json'
        with open(path,'w') as f:
            json.dump(obj=boxoffice_collection_daily,fp=f,indent=2)
        logger.info(f"Collection HTML page for run date: {date} saved to path: {path}")
        return path
    
    
def movie_page_extract(collection_parsed_fp,run_date:str): 
    
    movies_parsed=[]
    
    with open(collection_parsed_fp,'r') as f:
        collection_html_source:list[dict]
        collection_html_source=json.load(f)
    try:
        for i,movie_html in enumerate(collection_html_source):
            logger.info(f"Iteration: {i}, release id: {movie_html['release_id']}")
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
            movie_individual_dict['extracted_at']=movie_html['extracted_at']
            driver.get(movie_individual_dict['content']['url_boxofficemojo'])
            movie_individual_dict['content']['page_source']['boxofficemojo']=driver.page_source
            movie_soup=BeautifulSoup(movie_individual_dict['content']['page_source']['boxofficemojo'],features='html.parser')
            try:
                # Constructing the imdb movie page link
                movie_link_imdb="https://imdb.com"+movie_soup.select_one("#title-summary-refiner > a").attrs['href']
                movie_individual_dict['content']['movie_id']=movie_link_imdb.split('/')[-2]
                movie_individual_dict['content']['url_imdb']=movie_link_imdb
                driver.get(movie_link_imdb)
                movie_individual_dict['content']['page_source']['imdb']=driver.page_source
            except AttributeError as e:
                logger.error(f"Failed iteration {i} for movie release id: {movie_html['release_id']}")
                logger.exception(e)
                movie_individual_dict['content']['movie_id']=None
                logger.warning(f"List item: {i}, data point: 'movie_id' set to NONE")
                movie_individual_dict['content']['url_imdb']=None
                logger.warning(f"List item: {i}, data point: 'url_imdb' set to NONE")
                movie_individual_dict['content']['page_source']['imdb']=None
                logger.warning(f"List item: {i}, data point: 'page_source' set to NONE")
            
            movies_parsed.append(movie_individual_dict)
    except Exception as e:
            logger.error(f"Failed iteration {i} for movie release id: {movie_html['release_id']}")
            logger.exception(e)
    finally:
        path=f'run_{run_date}/movies_html_source_{run_date}.json'
        with open(path,'w') as f:
            json.dump(obj=movies_parsed,fp=f,indent=2)
        return path

def movie_cast_filmmakers_extract(parsed_movie_json_fp,run_date:str): # Takes the file path to individual movie and extracts and save the cast and crew info page from imdb.com to cast_pages directory
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
    try:
        for i,movie in enumerate(movies_parsed['content']):
            if movie['filmmakers']:
                for j,filmmaker in enumerate(movie['filmmakers']):
                    logger.info(f"movie iteration {i} and filmamker iteration {j} for movie_id : {movie['movie_id']} and filmmaker_id: {filmmaker['filmmaker_id']}")
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
                    if id:
                        for type,link in links.items():
                            driver.get(link)
                            filmmaker_dict['page_source'][type]['url']=link
                            filmmaker_dict['page_source'][type]['source']=driver.page_source
                    else:
                        logger.warning(f"filmmaker id is NONE in movie iteration {i} and filmmaker iteration {j}")
                        for type,_ in links.items():
                            filmmaker_dict['page_source'][type]['url']=None
                            filmmaker_dict['page_source'][type]['source']=None
                    
                    response['content'].append(filmmaker_dict)
            
            else:
                logger.warning(f"movie['filmmaker'] is NONE in iteration {i}")
    except Exception as e:
        logger.error(f"Failed movie iteration {i} and filmamker iteration {j} for movie_id : {movie['movie_id']} and filmmaker_id: {filmmaker['filmmaker_id']}")
        logger.exception(e)
    finally:    
        path=f"run_{run_date}/filmmaker_html_{run_date}.json"
        with open(path,'w') as f:
            json.dump(response,f,indent=2)

        return path
            
    
def genre_scraper(parsed_movie_json_fp,run_date:str):
    
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
    try:
        for i,movie in enumerate(movies_parsed['content']):
            if movie['genres']:
                for j,genre_id in enumerate(movie['genres']):
                    logger.info(f"movie_iteration: {i}, genre_iteration{j} for movie_id: {movie['movie_id']} and genre_id: {genre_id}")
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
            else:
                logger.warning("movie['genres'] is NONE")
    except Exception as e:
        logger.error(f"Failed movie_iteration: {i}, genre_iteration{j} for movie_id: {movie['movie_id']} and genre_id: {genre_id}")
        logger.exception(e)
    finally:
        path=f"run_{run_date}/genre_html_{run_date}.json"
        with open(path,'w') as f:
            json.dump(response,f,indent=2)
        
        return path



            

def distributor_scraper(movie_parsed_fp,run_date:str):
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

    try:
        for i,movie in enumerate(movies_parsed['content']):

            logger.info(f"Iteration: {i} and movie_id: {movie['movie_id']}")
            distributor_dict={}
            distributor_id=movie['distributor_id']
            distributor_dict['movie_id']=movie['movie_id']
            distributor_dict['distributor_id']=distributor_id

            if distributor_id:
                distributor_link_num_of_ratings=f"https://www.imdb.com/search/title/?title_type=feature&companies={distributor_id}&sort=num_votes,desc"
                driver.get(distributor_link_num_of_ratings)
                page_rating=driver.page_source
            

                distributor_link_us_box_office=f"https://www.imdb.com/search/title/?title_type=feature&companies={distributor_id}&sort=boxoffice_gross_us,desc"
                driver.get(distributor_link_us_box_office)
                page_collection=driver.page_source

            else:
                distributor_link_num_of_ratings=None
                distributor_link_us_box_office=None
                page_rating=None
                page_collection=None
                logger.warning(f"distributor id is NONE")

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
    except Exception as e:
        logger.error(f"Failed movie_iteration: {i} for movie_id: {movie['movie_id']} and distributor_id: {movie['distributor_id']}")
        logger.exception(e)
    finally:
        path=f"run_{run_date}/distributor_html_{run_date}.json"
        with open(path,'w') as f:
            json.dump(response,f,indent=2)
        
        return path



