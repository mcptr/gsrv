CREATE OR REPLACE FUNCTION api.game_create(
       _category TEXT,
       _min_players INTEGER,
       _max_players INTEGER DEFAULT NULL,
       _min_bid NUMERIC DEFAULT NULL,
       _max_bid NUMERIC DEFAULT NULL,
       _cost_to_join NUMERIC DEFAULT NULL
)
RETURNS storage.games
AS $$
DECLARE
	record_ storage.games;
BEGIN
	INSERT INTO storage.games(
	       category,
	       min_players,
	       max_players,
	       min_bid,
	       max_bid,
	       cost_to_join,
	       start_time
	) VALUES(
	       _category,
	       _min_players,
	       _max_players,
	       _min_bid,
	       _max_bid,
	       _cost_to_join,
	       future_utc_epoch((RANDOM() * 3)::INTEGER)
	)
	RETURNING * INTO record_;

	RETURN record_;
END
$$ LANGUAGE PLPGSQL STRICT;
