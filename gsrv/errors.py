class Error(Exception):
    pass


class AuthError(Error):
    def __init__(self, msg="Authentication error.", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
