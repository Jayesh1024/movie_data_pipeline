from bs4 import BeautifulSoup
import re
import random
import json
page_name="2024-09-01_daily_collection.html"
with open(f"html_files/{page_name}",'r') as f:
    soup=BeautifulSoup(f,features='html.parser')


def fact_parser(soup):
    outer_table=soup.select_one("#table > div > table.a-bordered.a-horizontal-stripes.a-size-base.a-span12.mojo-body-table.mojo-table-annotated.mojo-body-table-compact.scrolling-data-table > tbody")
    movie_rows=outer_table.find_all('tr')
    movie_fact_table=[]
    for i,row in enumerate(movie_rows):
        row_dict={}
        date_id=page_name.split("_")[0].replace('-','')
        #TODO add movie_id, num_releases,date_id and distributor_id key to row_dict

        if i>0 :
            cells=row.find_all('td')
            for j,cell in enumerate(cells):
                if j==0:
                    row_dict['rank']=cell.text
                elif j==2:
                    row_dict['movie_name']=cell.text
                elif j==3:
                    row_dict['collection_domestic']=cell.text
                elif j==6:
                    row_dict['num_theatres']=cell.text
                elif j==9:
                    row_dict['days_post_release']=cell.text
                elif j==10:
                    row_dict['distributor_name']=cell.text

            
            movie_fact_table.append(row_dict)

    return movie_fact_table


