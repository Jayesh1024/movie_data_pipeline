WITH source_target_join AS(
    SELECT
        s.genre_id genre_id_s,
        s.genre_name genre_name_s,
        s.top_movie_numofrating top_movie_numofrating_s,
        s.top_movie_us_boxoffice top_movie_us_boxoffice_s,
        s.total_movies total_movies_s,
        s.extracted_at extracted_at_s,
        s.effective_from effective_from_s,
        t.id id_t,
        t.genre_id genre_id_t,
        t.genre_name genre_name_t,
        t.total_movies total_movies_t,
        t.top_movie_numofrating top_movie_numofrating_t,
        t.top_movie_us_boxoffice top_movie_us_boxoffice_t,
        t.extracted_at extracted_at_t,
        t.effective_from effective_from_t,
        t.expiration_date expiration_date_t,
        t.active_inactive active_inactive_t
    FROM jayesh.dim_genre_staging s
    LEFT JOIN (SELECT * FROM jayesh.dim_genre WHERE active_inactive='active') t
    ON s.genre_id = t.genre_id
),
new_records AS(
    SELECT
        genre_id_s,
        genre_name_s,
        total_movies_s,
        top_movie_numofrating_s,
        top_movie_us_boxoffice_s,
        extracted_at_s,
        effective_from_s
    FROM source_target_join
    WHERE genre_id_t is null
),
scd2_records AS(
    SELECT
        genre_id_s,
        genre_name_s,
        total_movies_s,
        top_movie_numofrating_s,
        top_movie_us_boxoffice_s,
        extracted_at_s,
        effective_from_s
    FROM source_target_join
    WHERE
        genre_id_t is not null AND
        (
            top_movie_numofrating_s <> top_movie_numofrating_t OR
            top_movie_us_boxoffice_s <> top_movie_us_boxoffice_t
        )
),
scd1_records AS(
    SELECT
        genre_id_s,
        genre_name_s,
        total_movies_s,
        top_movie_numofrating_s,
        top_movie_us_boxoffice_s,
        extracted_at_s,
        effective_from_s
    FROM source_target_join
    WHERE
        genre_id_t is not null AND
        (
            total_movies_s <> total_movies_t AND
            top_movie_numofrating_s = top_movie_numofrating_t AND
            top_movie_us_boxoffice_s = top_movie_us_boxoffice_t            
        )
),
update_scd2 AS(
    UPDATE jayesh.dim_genre as g
    SET
        expiration_date = scd.effective_from_s,
        active_inactive = 'inactive'
    FROM scd2_records as scd
    WHERE
        g.genre_id IN (scd.genre_id_s) AND
        g.active_inactive = 'active'
    RETURNING *
),
insert_new_and_scd2 AS(
    INSERT INTO jayesh.dim_genre(
        genre_id,
        genre_name,
        total_movies,
        top_movie_numofrating,
        top_movie_us_boxoffice,
        extracted_at,
        effective_from
    )
    SELECT * FROM new_records
    UNION
    SELECT * FROM scd2_records
    RETURNING *
),
update_scd1 AS(
    UPDATE jayesh.dim_genre as g
    SET
        extracted_at = scd.extracted_at_s,
        total_movies = scd.total_movies_s
    FROM scd1_records as scd
    WHERE
        g.genre_id IN (scd.genre_id_s) AND
        g.active_inactive = 'active'
    RETURNING *
)

SELECT 1;

TRUNCATE dim_genre_staging;
