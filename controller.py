import extract
import parse
import json

def main():

    # Step 1
    date='2024-11-6'
    collection_html_json_path=extract.page_extract(date=date) # Returns the path of the json file which have the html data for the box office collection page for the run date

    # Step 2
    collection_parsed_path=parse.fact_parser(collection_html_json_path) # Returns the path of the parsed box office collection page for the run date

    # # Step 3
    movies_html_page_json_path=extract.movie_page_extract(collection_parsed_path) # Returns the path of the json file which have the movies pages for every movie on the collection page for input run date

    # Step 4
    movies_parsed_json_path=parse.movie_parser("movies_html_source_2024116.json") # Returns the path of the json file which have parsed movie page for every movie on the collections page for the input run date

    # # Step 5 (Can be run in parallel with filmmaker and distributor scraper and parser functions)
    genre_html_json_path=extract.genre_scraper(movies_parsed_json_path)
    genre_parsed_json_path=parse.genre_parser(genre_html_json_path)
    
    # # Step 6 (Parallel)
    filmmaker_html_json_path=extract.movie_cast_filmmakers_extract(movies_parsed_json_path)
    filmmaker_parsed_json_path=parse.filmmaker_parser(filmmaker_html_json_path)

    # Step 7 (Parallel)
    distributor_html_json_fp=extract.distributor_scraper("movies_parsed_2024116.json")
    distributor_parsed_json_fp=parse.distributor_parser(distributor_html_json_fp)

parse.filmmaker_parser("filmmaker_html_2024116.json")

#TODO: Log progress of genre, currently only movie progress is logged in the genre_scraper()