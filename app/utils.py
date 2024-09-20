

class AsyncIteratorWrapper:
    """ Utility class that transforms a
        regular iterable to an asynchronous one.
    """

    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value
