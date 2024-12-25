import sys
sys.path.append('/opt/src')
from parse import *
from extract import *
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task
import pendulum
from datetime import timedelta



with DAG(
    dag_id='movie_pipeline',
    schedule=timedelta(days=1),
    start_date=pendulum.datetime(2024,12,14,7,0,0,tz='Asia/Kolkata'),
    catchup=False
    
) as dag:
    
    def gen_dir(date):
        import os
        os.mkdir(f"./run_{date.replace('-','')}")
        return
    
    t1 = PythonOperator(
        task_id='create_run_dir',
        python_callable=gen_dir,
        op_args=["{{ds}}"]
    )

    t2 = PythonOperator(
        task_id='scrape_collection_page',
        python_callable=page_extract,
        op_args=["{{ds}}"]
    )

    t3 = PythonOperator(
        task_id='parse_collection_page',
        python_callable=fact_parser,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='scrape_collection_page')}}","{{ds.replace('-','')}}"]
    )

    t4= PythonOperator(
        task_id='scrape_movies',
        python_callable=movie_page_extract,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='parse_collection_page')}}","{{ds.replace('-','')}}"]
    )

    t5= PythonOperator(
        task_id='parse_movies',
        python_callable=movie_parser,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='scrape_movies')}}","{{ds.replace('-','')}}"]
    )

    t6= PythonOperator(
        task_id='scrape_genre',
        python_callable=genre_scraper,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='parse_movies')}}","{{ds.replace('-','')}}"]
    )
    t7= PythonOperator(
        task_id='parse_genre',
        python_callable=genre_parser,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='scrape_genre')}}","{{ds.replace('-','')}}"]
    )
    t8= PythonOperator(
        task_id='scrape_filmmakers',
        python_callable=movie_cast_filmmakers_extract,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='parse_movies')}}","{{ds.replace('-','')}}"]
    )
    t9= PythonOperator(
        task_id='parse_filmmakers',
        python_callable=filmmaker_parser,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='scrape_filmmakers')}}","{{ds.replace('-','')}}"]
    )
    t10= PythonOperator(
        task_id='scrape_distributors',
        python_callable=distributor_scraper,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='parse_movies')}}","{{ds.replace('-','')}}"]
    )
    t11= PythonOperator(
        task_id='parse_distributors',
        python_callable=distributor_parser,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='scrape_distributors')}}","{{ds.replace('-','')}}"]
    )

    
    t1>>t2>>t3>>t4>>t5>>[t6,t8,t10]
    t6>>t7
    t8>>t9
    t10>>t11