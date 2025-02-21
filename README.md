# Movie Data Pipeline

This is an ETL pipeline which scrapes data from the following sites:

1. boxofficemojo.com
2. imdb.com

And loads this data inside a PostgreSQL instance hosted on AWS Relational Database Service (RDS)

Following is the pipeline architecture:
![Architecture](misc/pipeline_arch.png "data pipeline architecture")

And, the following is the data model where the data will be loaded (click the image to open the link):
[![Movie Data Model](movieDataModel.png)](https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=dimensional_model.drawio&dark=auto#Uhttps%3A%2F%2Fraw.githubusercontent.com%2FJayesh1024%2Fmovie_data_pipeline%2Fmain%2Fdimensional_model.drawio)

