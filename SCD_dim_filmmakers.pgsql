WITH source_target_join AS(
    SELECT
        s.country country_s,
        s.debut_movie_id debut_movie_id_s,
        s.dob dob_s,
        s.filmmaker_id filmmaker_id_s,
        s.name name_s,
        s.place_of_birth place_of_birth_s,
        s.top_movie_numofrating top_movie_numofrating_s,
        s.top_movie_us_boxoffice top_movie_us_boxoffice_s,
        s.total_movies total_movies_s,
        s.extracted_at extracted_at_s,
        s.effective_from effective_from_s,
        s.age age_s,
        t.id id_t,
        t.filmmaker_id filmmaker_id_t,
        t.name name_t,
        t.dob dob_t,
        t.age age_t,
        t.place_of_birth place_of_birth_t,
        t.country country_t,
        t.total_movies total_movies_t,
        t.top_movie_numofrating top_movie_numofrating_t,
        t.top_movie_us_boxoffice top_movie_us_boxoffice_t,
        t.debut_movie_id debut_movie_id_t,
        t.extracted_at extracted_at_t,
        t.effective_from effective_from_t,
        t.expiration_date expiration_date_t,
        t.active_inactive active_inactive_t

    FROM jayesh.dim_filmmakers_staging s
    LEFT JOIN (SELECT * FROM jayesh.dim_filmmakers WHERE active_inactive='active') t
    ON s.filmmaker_id = t.filmmaker_id
),
new_records AS(
    SELECT
        country_s,
        debut_movie_id_s,
        dob_s,
        filmmaker_id_s,
        name_s,
        place_of_birth_s,
        top_movie_numofrating_s,
        top_movie_us_boxoffice_s,
        total_movies_s,
        extracted_at_s,
        effective_from_s,
        age_s
    FROM source_target_join
    WHERE filmmaker_id_t is null
),
scd1_records AS(
    SELECT
        country_s,
        debut_movie_id_s,
        dob_s,
        filmmaker_id_s,
        name_s,
        place_of_birth_s,
        top_movie_numofrating_s,
        top_movie_us_boxoffice_s,
        total_movies_s,
        extracted_at_s,
        effective_from_s,
        age_s
    FROM source_target_join
    WHERE
        filmmaker_id_t is not null AND
        (
            (
                age_s <> age_t OR
                total_movies_s <> total_movies_t
            ) AND
            top_movie_numofrating_s = top_movie_numofrating_t AND
            top_movie_us_boxoffice_s = top_movie_us_boxoffice_t
        )
),
scd2_records AS(
    SELECT
        country_s,
        debut_movie_id_s,
        dob_s,
        filmmaker_id_s,
        name_s,
        place_of_birth_s,
        top_movie_numofrating_s,
        top_movie_us_boxoffice_s,
        total_movies_s,
        extracted_at_s,
        effective_from_s,
        age_s
    FROM source_target_join
    WHERE
        filmmaker_id_t is not null AND
        (
            top_movie_numofrating_s <> top_movie_numofrating_t OR
            top_movie_us_boxoffice_s <> top_movie_us_boxoffice_t            
        )
),
update_scd2 AS(
    UPDATE jayesh.dim_filmmakers as f
    SET
        expiration_date = scd.effective_from_s,
        active_inactive = 'inactive'
    FROM scd2_records scd
    WHERE f.filmmaker_id IN (scd.filmmaker_id_s) AND active_inactive='active'
),
insert_rows AS(
    INSERT INTO jayesh.dim_filmmakers(
        country,
        debut_movie_id,
        dob,
        filmmaker_id,
        name,
        place_of_birth,
        top_movie_numofrating,
        top_movie_us_boxoffice,
        total_movies,
        extracted_at,
        effective_from,
        age
    )
    SELECT * FROM new_records
    UNION ALL
    SELECT * FROM scd2_records
    RETURNING *
),
update_scd1 AS(
    UPDATE jayesh.dim_filmmakers as f
    SET
        age = scd.age_s,
        total_movies = scd.total_movies_s,
        extracted_at = scd.extracted_at_s
    FROM scd1_records as scd
    WHERE f.filmmaker_id IN (scd.filmmaker_id_s) AND active_inactive = 'active'
)

SELECT 1;

TRUNCATE dim_filmmakers_staging;