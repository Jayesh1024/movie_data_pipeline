MERGE INTO jayesh.bridge_movie_filmmaker t
USING jayesh.bridge_movie_filmmaker_staging s
ON
    t.movie_id = s.movie_id AND
    t.filmmaker_id = s.filmmaker_id AND
    t.role = s.role

WHEN MATCHED THEN
    DO NOTHING
    
WHEN NOT MATCHED THEN
    INSERT(
        movie_id,
        filmmaker_id,
        role,
        effective_from
    )
    VALUES(
        s.movie_id,
        s.filmmaker_id,
        s.role,
        s.effective_from
    );

TRUNCATE bridge_movie_filmmaker_staging;