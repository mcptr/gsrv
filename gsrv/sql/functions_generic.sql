CREATE FUNCTION now_utc() RETURNS TIMESTAMP AS $$
       SELECT NOW() AT TIME ZONE 'UTC';
$$ LANGUAGE SQL;


CREATE FUNCTION to_epoch_utc(ts TIMESTAMP) RETURNS INTEGER AS $$
       SELECT EXTRACT(EPOCH FROM ts AT TIME ZONE 'UTC')::INTEGER;
$$ LANGUAGE SQL;


CREATE FUNCTION seconds_from_now_utc(ts TIMESTAMP) RETURNS INTEGER AS $$
       SELECT (EXTRACT(EPOCH FROM now_utc()) - EXTRACT(EPOCH FROM ts))::INTEGER;
$$ LANGUAGE SQL;


CREATE FUNCTION future_utc_epoch(seconds INTEGER) RETURNS TIMESTAMP WITH TIME ZONE AS $$
       SELECT to_timestamp(to_epoch_utc(now_utc()) + seconds)
$$ LANGUAGE SQL;


CREATE FUNCTION is_age_utc_sec(ts TIMESTAMP, sec INTEGER) RETURNS BOOLEAN AS $$
       SELECT seconds_from_now_utc(ts) >= sec;
$$ LANGUAGE SQL;


CREATE FUNCTION update_mtime() RETURNS TRIGGER AS $$
BEGIN
       NEW.mtime = now_utc();
       RETURN NEW;
END
$$ LANGUAGE PLPGSQL;



CREATE OR REPLACE FUNCTION hash_password() RETURNS TRIGGER
AS $$
BEGIN
    IF LENGTH(COALESCE(NEW.password, '')) < 6 THEN
       RAISE EXCEPTION 'Password too short/missing';
       RETURN NULL;
    END IF;

    IF substr(NEW.password, 1, 4) <> '$2a$' THEN
        NEW.password := crypt(NEW.password, gen_salt('bf'));
    END IF;

    NEW.email := LOWER(NEW.email);

    RETURN NEW;
END;
$$
LANGUAGE PLPGSQL STRICT;


CREATE OR REPLACE FUNCTION hash_api_key() RETURNS TRIGGER
AS $$
BEGIN
    IF LENGTH(COALESCE(NEW.api_key, '')) < 32 THEN
       RAISE EXCEPTION 'Api key too short (min: 32)';
       RETURN NULL;
    END IF;

    IF substr(NEW.api_key, 1, 4) <> '$2a$' THEN
        NEW.api_key := crypt(NEW.api_key, gen_salt('bf'));
    END IF;

    RETURN NEW;
END;
$$
LANGUAGE PLPGSQL STRICT;
