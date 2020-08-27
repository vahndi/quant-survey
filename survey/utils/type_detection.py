from typing import Iterable


def all_are(items: Iterable, item_type: type) -> bool:
    """
    Determine whether all items are of the given type.
    """
    return all([isinstance(item, item_type) for item in items])
