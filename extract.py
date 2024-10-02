from selenium import webdriver
import time
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
domain="https://boxofficemojo.com"
driver=webdriver.Chrome()

def page_extract(date):
    driver.get(f"https://www.boxofficemojo.com/date/{date}/")
    html_page=driver.page_source
    with open(f"html_files/{date}_daily_collection.html",'w') as f:
        f.write(html_page)
    
def movie_page_extract(collection_page_fp): # Takes the file path of daily collection page , extracts and save all the movies html page to movie_pages directory
    with open(collection_page_fp,'r') as f:
        soup_page=BeautifulSoup(f,features='html.parser')
    
    movie_anchor_tags=soup_page.select("#table > div > table.a-bordered.a-horizontal-stripes.a-size-base.a-span12.mojo-body-table.mojo-table-annotated.scrolling-data-table > tbody > tr:nth-child(n) > td.a-text-left.mojo-field-type-release.mojo-cell-wide > a")
    movie_links=[domain+tag.attrs['href'] for tag in movie_anchor_tags]
    for i,link in enumerate(movie_links):
        driver.get(link)
        movie_page=driver.page_source
        file_name=f"{collection_page_fp.split('/')[-1].split('_')[0]}_{movie_anchor_tags[i].text}.html"
        with open(f"movie_pages/{file_name}",'w') as f:
            f.write(movie_page)

def movie_cast_filmmakers_extract(movie_page_fp): # Takes the file path to individual movie and extracts and save the cast and crew info page from imdb.com to cast_pages directory
    with open(movie_page_fp,'r') as f:
        soup_movie=BeautifulSoup(f,features='html.parser')
    movie_imdb_link="https://imdb.com"+soup_movie.select_one("#title-summary-refiner > a").attrs['href']
    driver.get(movie_imdb_link)
    imdb_movie_page=driver.page_source
    soup_movie_imdb=BeautifulSoup(imdb_movie_page,features='html.parser')
    director_links=["https://imdb.com"+dir_anchor_tags.attrs['href'] for dir_anchor_tags in soup_movie_imdb.select("#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-afa4bed1-0.iMxoKo > section > div:nth-child(5) > section > section > div.sc-10bb6943-4.iWEGeT > div.sc-10bb6943-6.jDEuhp > div.sc-10bb6943-11.jcTGOi > div.sc-70a366cc-2.bscNnP > div > ul > li:nth-child(1) > div > ul > li:nth-child(n) > a")]
    writer_links=["https://imdb.com"+writer_anchor_tags.attrs['href'] for writer_anchor_tags in soup_movie_imdb.select("#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-afa4bed1-0.iMxoKo > section > div:nth-child(5) > section > section > div.sc-10bb6943-4.iWEGeT > div.sc-10bb6943-6.jDEuhp > div.sc-10bb6943-11.jcTGOi > div.sc-70a366cc-2.bscNnP > div > ul > li:nth-child(2) > div > ul > li:nth-child(n) > a")]
    cast_links=["https://imdb.com"+cast_anchor_tags.attrs['href'] for cast_anchor_tags in soup_movie_imdb.select("#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-afa4bed1-0.iMxoKo > section > div:nth-child(5) > section > section > div.sc-10bb6943-4.iWEGeT > div.sc-10bb6943-6.jDEuhp > div.sc-10bb6943-11.jcTGOi > div.sc-70a366cc-2.bscNnP > div > ul > li:nth-child(3) > div > ul > li:nth-child(n) > a")]

    for link in director_links:
        driver.get(link)
        director_page=driver.page_source
        with open(f"director_pages/{str(datetime.today().date())+"_"+link.split('/')[-2]}.html",'w') as f:
            f.write(director_page)
    
    for link in writer_links:
        driver.get(link)
        writer_page=driver.page_source
        with open(f"writer_pages/{str(datetime.today().date())+"_"+link.split('/')[-2]}.html",'w') as f:
            f.write(writer_page)
    
    for link in cast_links:
        driver.get(link)
        cast_page=driver.page_source
        with open(f"cast_pages/{str(datetime.today().date())+"_"+link.split('/')[-2]}.html",'w') as f:
            f.write(cast_page)
    
    


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


movie_cast_filmmakers_extract("movie_pages/2024-09-01_Alien: Romulus.html")