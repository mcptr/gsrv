CREATE OR REPLACE FUNCTION api.account_create(
       _account_id UUID,
       _api_key TEXT
) RETURNS BOOLEAN
AS $$
   BEGIN
	INSERT INTO auth.accounts(account_id, api_key)
	VALUES(_account_id, _api_key)
	ON CONFLICT(account_id) DO NOTHING;
	
	RETURN FOUND;
	END
$$ LANGUAGE PLPGSQL STRICT;


CREATE OR REPLACE FUNCTION api.account_get(_account_id UUID)
RETURNS Account_t
AS $$
   DECLARE record_ Account_t;
   BEGIN
	SELECT
		(account_id, is_enabled, balance)
		INTO record_
	FROM auth.accounts A
	WHERE A.account_id = _account_id
	      AND A.is_enabled;

	IF NOT FOUND THEN
	   RETURN NULL;
	END IF;

	record_.api_key = NULL;

	RETURN record_;
   END
$$ LANGUAGE PLPGSQL STRICT;


CREATE OR REPLACE FUNCTION api.authenticate(
       _account_id UUID,
       _api_key TEXT
       )
       RETURNS Account_t
AS $$
DECLARE _R Account_t;
BEGIN
	SELECT account_id, is_enabled, balance INTO _R
	FROM auth.accounts A
        WHERE A.account_id = _account_id
	      AND A.is_enabled
	      AND crypt(_api_key, A.api_key) = A.api_key;

	IF FOUND THEN
	   RETURN _R;
	END IF;
	
        RETURN NULL;
END;
$$
LANGUAGE PLPGSQL STRICT;
