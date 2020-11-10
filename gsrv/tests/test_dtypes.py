from gsrv.testing import Test
from gsrv.dtypes import Message, Auth

import uuid


class TestAuth(Test):
    def test_account_id(self):
        cases = [uuid.uuid4(), str(uuid.uuid4())]
        assert all([Auth(account_id=account_id) for account_id in cases])

    def test_invalid_account_id(self):
        cases = ["abdef", str(uuid.uuid4())[-2] + "Z", None, 123]
        for account_id in cases:
            with self.assertRaises(ValueError):
                Auth(account_id=account_id)


class TestMessage(Test):
    def test_message(self):
        msg = Message(
            text="test_message",
        )
        assert msg.auth is None

    def test_message_with_auth(self):
        msg = Message(
            text="test_message_with_auth",
            auth=Auth(
                account_id=uuid.uuid4(),
            )
        )
        assert msg.auth


if __name__ == "__main__":
    import unittest
    unittest.main()
