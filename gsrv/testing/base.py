import unittest
import testing.postgresql
from gsrv import pg
from gcore import cli


cli.setup_basic_logging()


Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)


def tearDownModule(self):
    Postgresql.clear_cache()


class BaseTest:
    ENABLE_POSTGRES = False
    POSTGRES_POOL_MINSIZE = 1
    POSTGRES_POOL_MAXSIZE = 5

    @classmethod
    def setUpClass(cls):
        cls.logger = cli.get_logger(cls.__name__)
        if cls.ENABLE_POSTGRES:
            cls.logger.debug("Starting postgresql server")
            cls._srv_pg = Postgresql()
            pg.initdb_sync(cls._srv_pg.url())

    @classmethod
    def tearDownClass(cls):
        if cls.ENABLE_POSTGRES:
            cls.logger.debug("Stopping postgresql server")
            cls._srv_pg.stop()


class AsyncTest(BaseTest, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        if self.ENABLE_POSTGRES:
            self.logger.debug("Creating pg pool")
            self.pgpool = await pg.create_pg_pool(
                self._srv_pg.url(),
                minsize=self.POSTGRES_POOL_MINSIZE,
                maxsize=self.POSTGRES_POOL_MAXSIZE,
            )

    async def asyncTearDown(self):
        if self.ENABLE_POSTGRES:
            self.logger.debug("Closing pg pool")
            await self.pgpool.close()
