import sys
sys.path.append('/opt/src/extract_scripts')
import os
from parse import *
from extract import *
from airflow.providers.databricks.operators.databricks import *
from airflow.providers.postgres.operators.postgres import *
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task
import pendulum
from datetime import timedelta

with DAG(
    dag_id='movie_pipeline',
    # schedule=timedelta(days=1),
    schedule=None,
    start_date=pendulum.datetime(2024,12,14,7,0,0,tz='Asia/Kolkata'),
    catchup=False
    
) as dag:
    run_date="{{(logical_date-macros.timedelta(days=2)).date()}}"
    run_date_no_dash="{{(logical_date-macros.timedelta(days=2)).strftime('%Y%m%d')}}"

    # def gen_dir(date):
    #     import os
    #     os.mkdir(f"./run_{date.replace('-','')}")
    #     return
    
    # t1 = PythonOperator(
    #     task_id='create_run_dir',
    #     python_callable=gen_dir,
    #     op_args=[run_date]
    # )

    t2 = PythonOperator(
        task_id='scrape_collection_page',
        python_callable=page_extract,
        op_args=[run_date]
    )

    t3 = PythonOperator(
        task_id='parse_collection_page',
        python_callable=fact_parser,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='scrape_collection_page')}}",run_date_no_dash]
    )

    t4= PythonOperator(
        task_id='scrape_movies',
        python_callable=movie_page_extract,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='parse_collection_page')}}",run_date_no_dash]
    )

    t5= PythonOperator(
        task_id='parse_movies',
        python_callable=movie_parser,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='scrape_movies')}}",run_date_no_dash]
    )

    t6= PythonOperator(
        task_id='scrape_genre',
        python_callable=genre_scraper,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='parse_movies')}}",run_date_no_dash]
    )
    t7= PythonOperator(
        task_id='parse_genre',
        python_callable=genre_parser,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='scrape_genre')}}",run_date_no_dash]
    )
    t8= PythonOperator(
        task_id='scrape_filmmakers',
        python_callable=movie_cast_filmmakers_extract,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='parse_movies')}}",run_date_no_dash]
    )
    t9= PythonOperator(
        task_id='parse_filmmakers',
        python_callable=filmmaker_parser,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='scrape_filmmakers')}}",run_date_no_dash]
    )
    t10= PythonOperator(
        task_id='scrape_distributors',
        python_callable=distributor_scraper,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='parse_movies')}}",run_date_no_dash]
    )
    t11= PythonOperator(
        task_id='parse_distributors',
        python_callable=distributor_parser,
        op_args=["{{ti.xcom_pull(key='return_value',task_ids='scrape_distributors')}}",run_date_no_dash]
    )
    new_cluster_spec={
        "num_workers": 0,
        "cluster_name": "",
        "spark_version": "15.4.x-scala2.12",
        "spark_conf": {
            "spark.master": "local[*, 4]",
            "spark.databricks.cluster.profile": "singleNode"
        },
        "aws_attributes": {
            "first_on_demand": 1,
            "availability": "SPOT_WITH_FALLBACK",
            "zone_id": "auto",
            "instance_profile_arn": None,
            "spot_bid_price_percent": 100
        },
        "node_type_id": "m5d.large",
        "driver_node_type_id": "m5d.large",
        "ssh_public_keys": [],
        "custom_tags": {
            "ResourceClass": "SingleNode"
        },
        "spark_env_vars": {
            "PYSPARK_PYTHON": "/databricks/python3/bin/python3"
        },
        "enable_elastic_disk": False,
        "init_scripts": [],
        "single_user_name": "jayeshsmhaske1@gmail.com",
        "data_security_mode": "SINGLE_USER",
        "runtime_engine": "STANDARD"
    }

    
    t12= DatabricksNotebookOperator(
        task_id='run_databricks_notebook',
        databricks_conn_id="databricks_default",
        notebook_path="/Workspace/Users/jayeshsmhaske1@gmail.com/transform",
        new_cluster=new_cluster_spec,
        source="WORKSPACE",
        notebook_params={
            "collection":"{{ti.xcom_pull(key='return_value',task_ids='parse_collection_page')}}",
            "movies":"{{ti.xcom_pull(key='return_value',task_ids='parse_movies')}}",
            "filmmaker":"{{ti.xcom_pull(key='return_value',task_ids='parse_filmmakers')}}",
            "genre":"{{ti.xcom_pull(key='return_value',task_ids='parse_genre')}}",
            "distributor":"{{ti.xcom_pull(key='return_value',task_ids='parse_distributors')}}"
        }
    )

    scripts=[os.path.join('load_scripts',name) for name in os.listdir('load_scripts')]

    sql_tasks=[]
    for script in scripts:
        with open(script,'r') as f:
            sql=f.read()
        sql_tasks.append(
            PostgresOperator(
            task_id=f'load_{script.split("/")[-1].split(".")[0]}',
            sql=sql
            ) 
        )
    t2>>t3>>t4>>t5>>[t6,t8,t10]
    t6>>t7
    t8>>t9
    t10>>t11
    [t7,t9,t11]>>t12>>sql_tasks
    
