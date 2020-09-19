from gsrv.testing import AsyncTest


class TestInitDB(AsyncTest):
    ENABLE_POSTGRES = True

    def test_load(self):
        print(self._srv_pg)


if __name__ == "__main__":
    import unittest
    unittest.main()
