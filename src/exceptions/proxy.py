from exceptions.base import AppError


class ProxyError(AppError):
    def __init__(self, *_: object) -> None:
        super().__init__("Proxy error was occured.")
