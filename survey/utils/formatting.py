from typing import List


def tab_indent(text: str) -> str:
    """
    Indent the text from the 2nd line onwards.

    :param text: The multi-line text to indent.
    """
    lines = text.split('\n')
    return '\n'.join(
        [lines[0]] + ['\t' + line for line in lines[1:]]
    )


def find_common_leading(strings: List[str]) -> str:
    """
    Find the common leading text in a list of strings.

    :param strings: List of strings to use.
    """
    shortest = min(len(string) for string in strings)
    ix = 0
    while len(set(string[ix] for string in strings)) == 1 and ix < shortest:
        ix += 1
    return strings[0][: ix]


def trim_common_leading(strings: List[str]) -> List[str]:
    """
    Trim common leading text from a list of strings.

    :param strings: List of strings to use.
    """
    num_leading = len(find_common_leading(strings))
    return [
        string[num_leading:] for string in strings
    ]


def find_common_trailing(strings: List[str]) -> str:
    """
    Find the common trailing text in a list of strings.

    :param strings: List of strings to use.
    """
    shortest = min(len(string) for string in strings)
    ix = -1
    while len(set(string[ix] for string in strings)) == 1 and -ix < shortest:
        ix -= 1
    return strings[0][ix + 1:]


def trim_common_trailing(strings: List[str]) -> List[str]:
    """
    Trim common leading text from a list of strings.

    :param strings: List of strings to use.
    """
    num_trailing = len(find_common_trailing(strings))
    return [
        string[:-num_trailing] for string in strings
    ]
