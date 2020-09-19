CREATE OR REPLACE FUNCTION api.session_create(_account_id UUID)
       RETURNS auth.sessions
AS $$
DECLARE
	record_ auth.sessions;
BEGIN
	INSERT INTO auth.sessions(account_id) VALUES(_account_id)
	RETURNING * INTO record_;

	RETURN record_;
END
$$ LANGUAGE PLPGSQL STRICT;
