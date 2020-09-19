CREATE OR REPLACE VIEW v_games_pending AS
       SELECT * FROM storage.games G
       WHERE NOT G.is_closed AND G.start_time > now_utc()
       ORDER BY G.ctime ASC;
