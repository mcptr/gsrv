from gsrv.runtime import RT
from gsrv.dtypes import Auth, Account


async def authenticate(rt: RT, auth: Auth) -> bool:
    if not auth:
        return None

    rt.get_logger(__name__).debug(auth.account_id)

    sql = "SELECT * FROM api.authenticate($1, $2)"
    async with rt.pgpool.acquire() as pgconn:
        async with pgconn.transaction():
            A = await pgconn.fetchrow(
                sql,
                str(auth.account_id),
                auth.api_key,
            )
            return (
                Account(account_id=A.get("account_id"))
                if A.get("account_id")
                else None
            )
