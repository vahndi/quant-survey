from typing import List


def bold_red(text: str) -> str:
    """
    Format the given text with a bold red style.
    """
    return '<b style="color:red">' + text + '</b>'


def bold_blue(text: str) -> str:
    """
    Format the given text with a bold blue style.
    """
    return '<b style="color:blue">' + text + '</b>'


def comma_and(items: List[str], capitalize: bool) -> str:
    """
    Return a list of items as a comma-separated string with "and" or "AND"
    separating the last 2 items.

    :param items: List of items to separate.
    :param capitalize: Whether to capitalize the separating "and" string.
    """
    str_and = ' AND ' if capitalize else ' and '
    if capitalize:
        items = [item.upper() for item in items]
    if len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return str_and.join(items)
    else:
        return str_and.join([', '.join(items[: -1]), items[-1]])


def comma_or(items: List[str], capitalize: bool, quotes: bool) -> str:
    """
    Return a list of items as a comma-separated string with "or" or "OR"
    separating the last 2 items.

    :param items: List of items to separate.
    :param capitalize: Whether to capitalize the separating "or" string.
    """
    str_or = ' OR ' if capitalize else ' or '
    if quotes:
        items = [f'"{item}"' for item in items]

    if len(items) == 0:
        raise ValueError('Must give at least one item.')
    elif len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return str_or.join(items)
    else:
        return str_or.join([', '.join(items[: -1]), items[-1]])


def spaces(num_spaces: int) -> str:
    """
    Return a string with the given number of spaces.
    """
    return ' ' * num_spaces
