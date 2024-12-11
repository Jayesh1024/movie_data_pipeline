WITH source_target_join AS(
    SELECT
        s.distributor_id distributor_id_s,
        s.distributor_name distributor_name_s,
        s.top_movie_numofrating top_movie_numofrating_s,
        s.top_movie_us_boxoffice top_movie_us_boxoffice_s,
        s.total_movies total_movies_s,
        s.extracted_at extracted_at_s,
        s.effective_from effective_from_s,
        t.distributor_id distributor_id_t,
        t.distributor_name distributor_name_t,
        t.total_movies total_movies_t,
        t.top_movie_numofrating top_movie_numofrating_t,
        t.top_movie_us_boxoffice top_movie_us_boxoffice_t,
        t.extracted_at extracted_at_t,
        t.effective_from effective_from_t,
        t.id id_t,
        t.expiration_date expiration_date_t,
        t.active_inactive active_inactive_t
    FROM jayesh.dim_distributor_staging s
    LEFT JOIN (SELECT * FROM jayesh.dim_distributor WHERE active_inactive='active') t
    ON s.distributor_id = t.distributor_id
),
new_records AS(
    SELECT
        distributor_id_s,
        distributor_name_s,
        top_movie_numofrating_s,
        top_movie_us_boxoffice_s,
        total_movies_s,
        extracted_at_s,
        effective_from_s
    FROM source_target_join
    WHERE distributor_id_t is null
),
scd2_records AS(
    SELECT
        distributor_id_s,
        distributor_name_s,
        top_movie_numofrating_s,
        top_movie_us_boxoffice_s,
        total_movies_s,
        extracted_at_s,
        effective_from_s
    FROM source_target_join
    WHERE
        distributor_id_t is not null AND
        (
            top_movie_numofrating_s <> top_movie_numofrating_t OR
            top_movie_us_boxoffice_s <> top_movie_us_boxoffice_t
        )
),
scd1_records AS(
    SELECT
        distributor_id_s,
        distributor_name_s,
        top_movie_numofrating_s,
        top_movie_us_boxoffice_s,
        total_movies_s,
        extracted_at_s,
        effective_from_s
    FROM source_target_join
    WHERE
        distributor_id_t is not null AND
        (
            total_movies_s <> total_movies_t AND
            top_movie_numofrating_s = top_movie_numofrating_t AND
            top_movie_us_boxoffice_s = top_movie_us_boxoffice_t            
        )
),
update_scd2 AS(
    UPDATE jayesh.dim_distributor as d
    SET
        expiration_date = scd.effective_from_s,
        active_inactive = 'inactive'
    FROM scd2_records as scd
    WHERE
        d.distributor_id IN (scd.distributor_id_s) AND
        d.active_inactive = 'active'
    RETURNING *
),
insert_new_and_scd2 AS(
    INSERT INTO jayesh.dim_distributor(
        distributor_id,
        distributor_name,
        top_movie_numofrating,
        top_movie_us_boxoffice,
        total_movies,
        extracted_at,
        effective_from
    )
    SELECT * FROM new_records
    UNION
    SELECT * FROM scd2_records
    RETURNING *
),
update_scd1 AS(
    UPDATE jayesh.dim_distributor as d
    SET
        extracted_at = scd.extracted_at_s,
        total_movies = scd.total_movies_s
    FROM scd1_records as scd
    WHERE
        d.distributor_id IN (scd.distributor_id_s) AND
        d.active_inactive = 'active'
    RETURNING *
)

SELECT '1';

TRUNCATE dim_distributor_staging;