-- SCD1 implementation for jayesh.dim_movies table
MERGE INTO jayesh.dim_movies AS t
USING jayesh.dim_movies_staging AS s
ON t.movie_id=s.movie_id

WHEN MATCHED AND (t.post_release_days<>s.post_release_days OR
                    t.imdb_rating<>s.imdb_rating OR
                    t.num_of_rating<>s.num_of_rating
)
THEN
    UPDATE SET 
            post_release_days=s.post_release_days,
            imdb_rating=s.imdb_rating,
            num_of_rating=s.num_of_rating,
            effective_from=s.effective_from,
            extracted_at=s.extracted_at


WHEN NOT MATCHED
THEN
    INSERT VALUES(
        DEFAULT,
        s.movie_id,
        s.release_id,
        s.movie_name,
        s.release_date_id,
        s.rating,
        s.duration,
        s.post_release_days,
        s.widest_release,
        s.imdb_rating,
        s.num_of_rating,
        s.distributor_id,
        s.effective_from,
        s.extracted_at
    );

TRUNCATE dim_movies_staging;


