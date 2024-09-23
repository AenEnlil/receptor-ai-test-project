import ast

dangerous_words = ['import', 'os', 'system', 'open', 'from', 'while', 'range', 'Interpreter', 'runsource',
                   'locals', 'globals']


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


def check_for_dangerous_code(code_string: str) -> bool:
    """ Checks code string for dangerous code

    :param code_string: code string that will be checked for dangerous code
    :return: returns boolean result of check
    """
    for word in dangerous_words:
        if word in code_string:
            return False
    return True


def check_if_syntax_is_correct(code_string):
    """ Checks code string for errors in syntax

    :param code_string: code string that will be checked for syntax error
    :return: returns boolean result of check
    """
    try:
        ast.parse(code_string, mode='exec')
        return True
    except SyntaxError:
        return False
