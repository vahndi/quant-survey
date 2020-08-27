from pandas import Series, DataFrame

from survey.compound_types import GroupPairs


def get_group_pairs(
        items: list, ordered: bool, include_empty: bool
) -> GroupPairs:
    """
    Return all ordered groupings of the items into 2 groups.

    :param items: The items to use.
    :param ordered: Whether to restrict the groupings to only ordered items.
    :param include_empty: Whether to include empty lists as one of the groups.
    """

    def _get_groups(bin_str: str):
        group_indices = [int(c) for c in bin_str]
        group_0, group_1 = [], []
        for group_index, item in zip(group_indices, items):
            if group_index == 0:
                group_0.append(item)
            else:
                group_1.append(item)
        return group_0, group_1

    # set bounds
    num_items = len(items)
    if include_empty:
        i_start, i_end = 0, 2 ** num_items
    else:
        i_start, i_end = 1, 2 ** num_items - 1
    # generate pairs
    pairs = []
    if ordered:
        for i in range(i_start, i_end):
            bin_string = f'{i:b}'.zfill(num_items)
            num_zeros = bin_string.count('0')
            num_ones = num_items - num_zeros
            zeros_left = bin_string[: num_zeros].count('0')
            ones_left = bin_string[: num_ones].count('1')
            if (
                    (zeros_left > 0 and zeros_left == num_zeros) or
                    (ones_left > 0 and ones_left == num_ones)
            ):
                pairs.append(_get_groups(bin_string))
    else:
        for i in range(i_start, i_end):
            bin_string = f'{i:b}'.zfill(num_items)
            pairs.append(_get_groups(bin_string))

    return pairs


def match_all(data: DataFrame, match: dict, exclude_ix=None) -> Series:
    """
    Calculate a series that can be used to index into the rows of the data
    where all of the values in the dict equal the equivalent values in the
    columns.

    :param data:  The DataFrame containing the data to return an indexer for.
    :param match: Dict of values where the keys are columns of the dataframe and
                  values are the values to match.
    :param exclude_ix: Optional index value to exclude from matching.
    """
    # create an index to match all
    ix_match = Series(data=[True]*len(data), index=data.index)
    # subtract rows where column value != match dict value
    for key, value in match.items():
        ix_match = ix_match & (data[key] == value)
    # drop excluded index values
    if exclude_ix is not None:
        ix_match.loc[exclude_ix] = False
    return ix_match
