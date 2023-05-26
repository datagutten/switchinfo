class APIError(Exception):
    pass


class LoginFailed(APIError):
    def __str__(self):
        return 'Login failed'
