CREATE TYPE GameCategory_t AS ENUM(
       'ANAGRAMS', 'ANAGRAMS_8', 'ANAGRAMS_12', 'ANAGRAMS_16',
       'HANGMAN',  'HANGMAN_8',  'HANGMAN_12',  'HANGMAN_16',
       'HANGRAMS', 'HANGRAMS_8', 'HANGRAMS_12', 'HANGRAMS_16'
);

CREATE TYPE GameStatus_t AS ENUM(
       'NEW', 'READY', 'IN_PROGRESS', 'COMPLETE', 'ERROR'
);


CREATE TYPE Account_t AS (
       account_id UUID,
       is_enabled BOOLEAN,
       balance NUMERIC(16,0)
);
