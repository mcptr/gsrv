CREATE TABLE IF NOT EXISTS auth.accounts (
       account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       api_key TEXT NOT NULL,
       email TEXT DEFAULT NULL,
       balance NUMERIC(16,8) DEFAULT NULL,
       is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
       ctime TIMESTAMP NOT NULL DEFAULT now_utc(),
       mtime TIMESTAMP DEFAULT NULL
);


CREATE TRIGGER trg_hash_api_key
       BEFORE UPDATE OR INSERT ON auth.accounts
       FOR EACH ROW EXECUTE PROCEDURE hash_api_key();


CREATE TRIGGER trg_update_mtime BEFORE INSERT OR UPDATE
       ON auth.accounts FOR EACH ROW
       EXECUTE PROCEDURE update_mtime();

CREATE TABLE IF NOT EXISTS auth.sessions (
       session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       account_id UUID DEFAULT NULL REFERENCES auth.accounts(account_id)
       		  ON UPDATE CASCADE ON DELETE CASCADE,
       storage TEXT DEFAULT NULL,
       ctime TIMESTAMP NOT NULL DEFAULT now_utc(),
       mtime TIMESTAMP DEFAULT NULL
);


CREATE UNIQUE INDEX session_uidx ON auth.sessions(session_id, account_id);


CREATE TRIGGER trg_update_mtime BEFORE INSERT OR UPDATE
       ON auth.sessions FOR EACH ROW
       EXECUTE PROCEDURE update_mtime();


CREATE TABLE IF NOT EXISTS storage.players (
       player_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       account_id UUID DEFAULT NULL, -- FIXME: REF
       ctime TIMESTAMP NOT NULL DEFAULT now_utc(),
       mtime TIMESTAMP DEFAULT NULL
);


CREATE TABLE IF NOT EXISTS storage.games (
       game_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       category TEXT NOT NULL,
       is_closed BOOLEAN DEFAULT FALSE,
       min_players INTEGER NOT NULL DEFAULT 1,
       max_players INTEGER NOT NULL DEFAULT 1,
       min_bid NUMERIC(16,8) NOT NULL DEFAULT 1,
       max_bid NUMERIC(16,8) NOT NULL DEFAULT 1,
       cost_to_join NUMERIC(16,8) NOT NULL DEFAULT 0,
       start_time TIMESTAMP NOT NULL DEFAULT future_utc_epoch(5),
       ctime TIMESTAMP NOT NULL DEFAULT now_utc(),
       mtime TIMESTAMP DEFAULT NULL
);


CREATE TRIGGER trg_update_mtime BEFORE INSERT OR UPDATE
       ON storage.games FOR EACH ROW
       EXECUTE PROCEDURE update_mtime();


CREATE TABLE IF NOT EXISTS storage.game_players(
       game_id UUID NOT NULL REFERENCES storage.games(game_id),
       player_id UUID NOT NULL REFERENCES storage.players(player_id),
       ctime TIMESTAMP NOT NULL DEFAULT now_utc()
);

CREATE UNIQUE INDEX unique_player_in_game_uidx ON storage.game_players(game_id, player_id);
