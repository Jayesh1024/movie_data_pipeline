from selenium import webdriver
import time
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
domain="https://boxofficemojo.com"
driver=webdriver.Chrome()

def page_extract(date):
    '''
    Saves the daily box office collection page of boxofficemojo.com to daily_box_office/ for input date

    :type date: str
    :param date: date for which to save the box office collection html page
    '''
    driver.get(f"https://www.boxofficemojo.com/date/{date}/")
    html_page=driver.page_source
    with open(f"daily_box_office/{date}_daily_collection.html",'w') as f:
        f.write(html_page)
    
def movie_page_extract(collection_page_fp): 
    '''
    Saves the html page for every movie in the given box office collection html page file path to movie_pages/

    :type collection_page_fp: str
    :param collection_page_fp: file path of the box office collection html page
    
    '''
    with open(collection_page_fp,'r') as f:
        soup_page=BeautifulSoup(f,features='html.parser')
    
    movie_anchor_tags=soup_page.select("#table > div > table.a-bordered.a-horizontal-stripes.a-size-base.a-span12.mojo-body-table.mojo-table-annotated.scrolling-data-table > tbody > tr:nth-child(n) > td.a-text-left.mojo-field-type-release.mojo-cell-wide > a")
    movie_links=[domain+tag.attrs['href'] for tag in movie_anchor_tags]
    for i,link in enumerate(movie_links):
        driver.get(link)
        movie_page=driver.page_source
        movie_soup=BeautifulSoup(movie_page,features='html.parser')
        movie_link_imdb="https://imdb.com"+movie_soup.select_one("#title-summary-refiner > a").attrs['href']
        driver.get(movie_link_imdb)
        movie_page_imdb=driver.page_source
        
        file_name=movie_link_imdb.split('/')[-2]
        with open(f"movie_pages/{file_name}.html",'w') as f:
            f.write(movie_page)
        with open(f"movie_pages/{file_name}_imdb.html",'w') as f:
            f.write(movie_page_imdb)

def movie_cast_filmmakers_extract(movie_page_fp): # Takes the file path to individual movie and extracts and save the cast and crew info page from imdb.com to cast_pages directory
    with open(movie_page_fp,'r') as f:
        soup_movie=BeautifulSoup(f,features='html.parser')
    movie_imdb_link="https://imdb.com"+soup_movie.select_one("#title-summary-refiner > a").attrs['href']
    driver.get(movie_imdb_link)
    imdb_movie_page=driver.page_source
    soup_movie_imdb=BeautifulSoup(imdb_movie_page,features='html.parser')
    filmmakers={
        "director_links":["https://imdb.com"+dir_anchor_tags.attrs['href'] for dir_anchor_tags in soup_movie_imdb.select("#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-afa4bed1-0.iMxoKo > section > div:nth-child(5) > section > section > div:nth-child(3) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div > ul > li:nth-child(1) > div > ul > li:nth-child(n) > a")],
        "writer_links":["https://imdb.com"+writer_anchor_tags.attrs['href'] for writer_anchor_tags in soup_movie_imdb.select("#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-afa4bed1-0.iMxoKo > section > div:nth-child(5) > section > section > div:nth-child(3) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div > ul > li:nth-child(2) > div > ul > li:nth-child(n) > a")],
        "cast_links":["https://imdb.com"+cast_anchor_tags.attrs['href'] for cast_anchor_tags in soup_movie_imdb.select("#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-afa4bed1-0.iMxoKo > section > div:nth-child(5) > section > section > div:nth-child(3) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div > ul > li:nth-child(3) > div > ul > li:nth-child(n) > a")]
    }

    def save_filmmaker_info(id):
        '''
        Saves the html pages for the given filmmaker id to dir :filmmaker_pages/

        :type id: str
        :type directory_name: str
        :param id: id of the filmmaker, can be a start, director or writer
        :param directory_name: directory where the pages need to be saved
        '''
        links={
            "profile_link":f"https://www.imdb.com/name/{id}/",
            "search_num_of_ratings":f"https://www.imdb.com/search/title/?title_type=feature&role={id}&sort=num_votes,desc",
            "search_box_office":f"https://www.imdb.com/search/title/?title_type=feature&role={id}&sort=boxoffice_gross_us,desc",
            "search_debut_movie":f"https://www.imdb.com/search/title/?title_type=feature&role={id}&sort=release_date,asc"
        }
        for link_type,link in links.items():
            driver.get(link)
            page=driver.page_source
            with open(f"filmmaker_pages/{link_type}_{id}.html",'w') as f:
                f.write(page)

    for _,links in filmmakers.items():
        for link in links:
            id=link.split('/')[-2]
            save_filmmaker_info(id=id)
    
def genre_scraper(movie_page_fp):
    '''
    Saves the genre page html file by number of ratings and us box office collection.\n
    For every genre page there are two sorting types\n
    1. Number of rating sorting types are stored in genre_pages_num_of_rating/\n
    2. US box office collection sorting types are stored in genre_pages_us_box_office/


    :type: str
    :param movie_page_fp: movie page html file path (located in movie_pages/)
    
    '''
    with open(movie_page_fp,'r') as f:
        soup_movie=BeautifulSoup(f,features='html.parser')
    movie_imdb_link="https://imdb.com"+soup_movie.select_one("#title-summary-refiner > a").attrs['href']
    driver.get(movie_imdb_link)
    imdb_movie_page=driver.page_source
    soup_movie_imdb=BeautifulSoup(imdb_movie_page,features='html.parser')


    genre_anchors=soup_movie_imdb.select("#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-afa4bed1-0.iMxoKo > section > div:nth-child(5) > section > section > div:nth-child(3) > div:nth-child(2) > div:nth-child(1) > section > div:nth-child(1) > div.ipc-chip-list__scroller > a:nth-child(n)")
    for anchor in genre_anchors:
        genre_id=anchor.attrs['href'].split('/')[-2]

        genre_link_num_of_rating_sorted=f"https://www.imdb.com/search/title/?title_type=feature&interests={genre_id}&sort=num_votes,desc"
        driver.get(genre_link_num_of_rating_sorted)
        genre_page=driver.page_source
        with open(f"genre_pages_num_of_rating/{genre_id}_num_of_rating.html",'w') as f:
            f.write(genre_page)

        genre_link_us_box_office_collection_sorted=f"https://www.imdb.com/search/title/?title_type=feature&interests={genre_id}&sort=boxoffice_gross_us,desc"
        driver.get(genre_link_us_box_office_collection_sorted)
        genre_page=driver.page_source
        with open(f"genre_pages_us_box_office/{genre_id}_us_box_office.html",'w') as f:
            f.write(genre_page)

def distributor_scraper(movie_page_fp):
    '''
    Saves the distributor html page for following sort types to get top movies by\n
    1. Number of ratings\n Saves to distributor_pages_num_of_rating/\n
    2. US box office collection\n Saves to distributor_pages_us_box_office/

    :type movie_page_fp: str
    :param movie_page_fp: movie page file path of box office mojo site

    '''
    with open(movie_page_fp,'r') as f:
        soup_movie=BeautifulSoup(f,features='html.parser')
    distributor_id=soup_movie.select_one("#a-page > main > div > div.a-section.a-spacing-none.mojo-gutter.mojo-summary-table > div.a-section.a-spacing-none.mojo-summary-values.mojo-hidden-from-mobile > div:nth-child(1) > span:nth-child(2) > a").attrs['href'].split('/')[-3]

    distributor_link_num_of_ratings=f"https://www.imdb.com/search/title/?title_type=feature&companies={distributor_id}&sort=num_votes,desc"
    driver.get(distributor_link_num_of_ratings)
    page=driver.page_source
    with open(f"distributor_pages_num_of_rating/{distributor_id}_num_of_ratings.html",'w') as f:
        f.write(page)

    distributor_link_us_box_office=f"https://www.imdb.com/search/title/?title_type=feature&companies={distributor_id}&sort=boxoffice_gross_us,desc"
    driver.get(distributor_link_us_box_office)
    page=driver.page_source
    with open(f"distributor_pages_us_box_office/{distributor_id}_box_office_us.html",'w') as f:
        f.write(page)
    

def main():
    
    start_date="2024-09-01"
    end_date="2024-09-23"

    dates=[] # Stores the date, starting from start_date to end_date

    start_date_object=datetime.strptime(start_date,"%Y-%m-%d").date()
    end_date_object=datetime.strptime(end_date,"%Y-%m-%d").date()

    while start_date_object<=end_date_object:
        page_extract(str(start_date_object))
        start_date_object=start_date_object+timedelta(1)
    driver.close()


movie_cast_filmmakers_extract('movie_pages/tt11315808.html')