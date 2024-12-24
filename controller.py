import argparse
import extract
import parse
import os
from log import logger

parser=argparse.ArgumentParser()
parser.add_argument("--run_date",type=str,required=True)

args=parser.parse_args()

print(args.run_date)
def main():
    try:
        # Step 1
        run_date=args.run_date # Date for which the data will be scraped from the sites
        run_date_str=run_date.replace('-','')
        os.mkdir(f"./run_{run_date_str}")
        collection_html_json_path=extract.page_extract(date=run_date) # Returns the path of the json file which have the html data for the box office collection page for the run date

        # Step 2
        collection_parsed_path=parse.fact_parser(collection_html_json_path,run_date_str) # Returns the path of the parsed box office collection page for the run date

        # # Step 3
        movies_html_page_json_path=extract.movie_page_extract(collection_parsed_path,run_date_str) # Returns the path of the json file which have the movies pages for every movie on the collection page for input run date

        # Step 4
        movies_parsed_json_path=parse.movie_parser(movies_html_page_json_path,run_date_str) # Returns the path of the json file which have parsed movie page for every movie on the collections page for the input run date

        # # Step 5 (Can be run in parallel with filmmaker and distributor scraper and parser functions)
        genre_html_json_path=extract.genre_scraper(movies_parsed_json_path,run_date_str)
        genre_parsed_json_path=parse.genre_parser(genre_html_json_path,run_date_str)
        
        # # Step 6 (Parallel)
        filmmaker_html_json_path=extract.movie_cast_filmmakers_extract(movies_parsed_json_path,run_date_str)
        filmmaker_parsed_json_path=parse.filmmaker_parser(filmmaker_html_json_path,run_date_str)

        # Step 7 (Parallel)
        distributor_html_json_fp=extract.distributor_scraper(movies_parsed_json_path,run_date_str)
        distributor_parsed_json_fp=parse.distributor_parser(distributor_html_json_fp,run_date_str)
    except Exception as e:
        logger.exception(e)

