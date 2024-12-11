MERGE INTO jayesh.bridge_movie_genre t
USING jayesh.bridge_movie_genre_staging s
ON
    s.movie_id = t.movie_id AND
    s.genre_id = t.movie_id

WHEN MATCHED THEN
    DO NOTHING

WHEN NOT MATCHED THEN
    INSERT(
        movie_id,
        genre_id,
        effective_from
    )
    VALUES(
        s.movie_id,
        s.genre_id,
        s.effective_from
    );

TRUNCATE bridge_movie_genre_staging;