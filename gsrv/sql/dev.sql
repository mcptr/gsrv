CREATE OR REPLACE FUNCTION pg_temp.sortarray(int2[]) RETURNS int2[]
AS $$
  SELECT ARRAY(
      SELECT $1[i]
        FROM generate_series(array_lower($1, 1), array_upper($1, 1)) i
    ORDER BY 1
  )
$$ LANGUAGE SQL;

CREATE OR REPLACE VIEW v_missing_indexes AS
    SELECT conrelid::regclass,
	   conname,
	   reltuples::bigint
    FROM pg_constraint
	  JOIN pg_class ON (conrelid = pg_class.oid)
    WHERE contype = 'f'
	  AND NOT EXISTS (
	      SELECT 1
	      FROM pg_index
	      WHERE indrelid = conrelid
		  AND pg_temp.sortarray(conkey) = pg_temp.sortarray(indkey)
	 )
    ORDER BY reltuples DESC;


CREATE OR REPLACE VIEW v_db_info AS
   SELECT table_schema,
	  table_name,
	  pg_size_pretty(pg_total_relation_size(table_name::regclass)) AS table_size
	  -- pg_size_pretty (pg_indexes_size('user_jobs')) AS idx_size
   FROM information_schema.tables
   WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
	 AND table_type = 'BASE TABLE'
   ORDER BY table_schema,
	    table_name;
