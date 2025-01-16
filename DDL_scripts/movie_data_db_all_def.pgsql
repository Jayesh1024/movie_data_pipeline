
-- Orchestrate the whole thing
-- Performance optimisation strategies: Indexing, Partitioning, Clustering, or Aggregations

CREATE SCHEMA jayesh;


CREATE TABLE jayesh.dim_distributor (
    id integer NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    distributor_id character varying(30) NOT NULL,
    distributor_name character varying(50),
    total_movies integer,
    top_movie_numofrating character varying(30),
    top_movie_us_boxoffice character varying(30),
    extracted_at bigint,
    effective_from bigint,
    expiration_date bigint DEFAULT '99991231'::bigint,
    active_inactive character varying(30) DEFAULT 'active'::character varying
);



CREATE TABLE jayesh.dim_distributor_staging (
    distributor_id character varying(30) NOT NULL PRIMARY KEY,
    distributor_name character varying(50),
    total_movies integer,
    top_movie_numofrating character varying(30),
    top_movie_us_boxoffice character varying(30),
    extracted_at bigint,
    effective_from bigint
);





CREATE TABLE jayesh.dim_filmmakers (
    id integer NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    filmmaker_id character varying(30) NOT NULL,
    name character varying(50),
    dob date,
    age integer,
    place_of_birth character varying(100),
    country character varying(30),
    total_movies integer,
    top_movie_numofrating character varying(30),
    top_movie_us_boxoffice character varying(30),
    debut_movie_id character varying(30),
    extracted_at bigint,
    effective_from bigint,
    expiration_date bigint DEFAULT '99991231'::bigint,
    active_inactive character varying(30) DEFAULT 'active'::character varying
);



CREATE TABLE jayesh.dim_filmmakers_staging (
    filmmaker_id character varying(30) NOT NULL PRIMARY KEY,
    name character varying(50),
    dob date,
    age integer,
    place_of_birth character varying(100),
    country character varying(30),
    total_movies integer,
    top_movie_numofrating character varying(30),
    top_movie_us_boxoffice character varying(30),
    debut_movie_id character varying(30),
    extracted_at bigint,
    effective_from bigint
);




CREATE TABLE jayesh.dim_genre (
    id integer NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    genre_id character varying(30) NOT NULL,
    genre_name character varying(30),
    total_movies integer,
    top_movie_numofrating character varying(30),
    top_movie_us_boxoffice character varying(30),
    extracted_at bigint,
    effective_from bigint,
    expiration_date bigint DEFAULT '99991231'::bigint,
    active_inactive character varying(30) DEFAULT 'active'::character varying
);



CREATE TABLE jayesh.dim_genre_staging (
    genre_id character varying(30) NOT NULL PRIMARY KEY,
    genre_name character varying(30),
    total_movies integer,
    top_movie_numofrating character varying(30),
    top_movie_us_boxoffice character varying(30),
    extracted_at bigint,
    effective_from bigint
);




CREATE TABLE jayesh.dim_movies (
    id integer NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    movie_id character varying(30) NOT NULL,
    release_id character varying(30),
    movie_name character varying(100),
    release_date_id bigint,
    rating character varying(30),
    duration integer,
    post_release_days integer,
    widest_release integer,
    imdb_rating real,
    num_of_rating bigint,
    distributor_id character varying(30),
    effective_from bigint,
    extracted_at bigint
);



CREATE TABLE jayesh.dim_movies_staging (
    movie_id character varying(30) NOT NULL PRIMARY KEY,
    release_id character varying(30),
    movie_name character varying(100),
    release_date_id bigint,
    rating character varying(30),
    duration integer,
    post_release_days integer,
    widest_release integer,
    imdb_rating real,
    num_of_rating bigint,
    distributor_id character varying(30),
    effective_from bigint,
    extracted_at bigint
);




CREATE TABLE jayesh.fact_domestic_collection (
    id integer NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    effective_from integer,
    movie_id character varying(30) NOT NULL,
    release_id character varying(30) NOT NULL,
    days_post_release integer,
    num_theatres integer,
    collection_domestic double precision,
    num_of_releases integer,
    rank integer,
    extracted_at bigint
);



CREATE TABLE jayesh.bridge_movie_filmmaker (
    movie_id character varying(30) NOT NULL,
    filmmaker_id character varying(30) NOT NULL,
    role character varying(30),
    effective_from bigint
);




CREATE TABLE jayesh.bridge_movie_filmmaker_staging (
    movie_id character varying(30) NOT NULL,
    filmmaker_id character varying(30) NOT NULL,
    role character varying(30),
    effective_from bigint
);



CREATE TABLE jayesh.bridge_movie_genre (
    movie_id character varying(30) NOT NULL,
    genre_id character varying(30) NOT NULL,
    effective_from bigint
);


CREATE TABLE jayesh.bridge_movie_genre_staging (
    movie_id character varying(30) NOT NULL,
    genre_id character varying(30) NOT NULL,
    effective_from bigint
);


