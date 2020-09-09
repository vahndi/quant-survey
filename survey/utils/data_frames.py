from itertools import product

from numpy import nan
from pandas import DataFrame, pivot_table, Series, concat, MultiIndex, merge
from typing import Callable, List, Union


def sort_data_frame_values(data: DataFrame, sort_by: Union[List, Callable, str],
                           ascending: bool = True) -> DataFrame:
    """
    Extension to pandas sort_values method that allows lambda functions.

    :param data: DataFrame to sort_values.
    :param sort_by: str or lambda or list of strs and/or lambdas
                    e.g. lambda d: d['1'] + d['2']
    :param ascending: Whether to sort ascending or descending
    """
    if type(sort_by) is str or callable(sort_by):
        sort_by = [sort_by]
    for col in reversed(sort_by):
        if type(col) is str:
            data = data.sort_values(col, ascending=ascending)
        elif callable(col):
            data['tmp_sort_col'] = col(data)
            data = data.sort_values('tmp_sort_col', ascending=ascending)
            data = data.drop('tmp_sort_col', axis=1)
        else:
            raise TypeError(f'Cannot sort by type {type(sort_by)}')
    return data


def count_coincidences(
        data_1: Union[DataFrame, Series],
        data_2: Union[DataFrame, Series],
        column_1: str, column_2: str,
        column_1_order: List[str], column_2_order: List[str]
) -> DataFrame:
    """
    Count the number of times each value of column 1 appears with each value of
    column 2.

    :param data_1: The DataFrame or Series containing the first distribution.
    :param data_2: The DataFrame or Series containing the second distribution.
    :param column_1: The name of the first column.
    :param column_2: The name of the second column.
    :param column_1_order: The order to sort values in the first column.
    :param column_2_order: The order to sort values in the second column.
    :return: DataFrame with column_1 values as columns and column_2 values as
             index, sorted by the given order.
    """
    data_1 = data_1.copy()
    data_2 = data_2.copy()
    # validate inputs
    if (
            isinstance(data_1, Series) and
            isinstance(data_2, Series) and
            data_1.name == data_2.name
    ):
        raise ValueError('data_1 and data_2 must have different names'
                         ' if they are both Series')
    is_multi_1 = isinstance(data_1.index, MultiIndex)
    is_multi_2 = isinstance(data_2.index, MultiIndex)
    if isinstance(data_1, DataFrame):
        for col in data_1.columns:
            data_1[col] = data_1[col].replace({1: col, 0: nan})
    elif isinstance(data_1, Series):
        if data_1.name is None:
            raise ValueError('data_1 must be named')
        if is_multi_1:
            if None in data_1.index.names:
                raise ValueError(
                    'each index in data_1 MultiIndex must be named'
                )
        else:
            if data_1.index.name is None:
                raise ValueError('data_1 index must be named')
    else:
        raise TypeError('data_1 must be Series or DataFrame')
    if isinstance(data_2, DataFrame):
        for col in data_2.columns:
            data_2[col] = data_2[col].replace({1: col, 0: nan})
    elif isinstance(data_2, Series):
        if data_2.name is None:
            raise ValueError('data_1 must be named')
        if is_multi_2:
            if None in data_2.index.names:
                raise ValueError(
                    'each index in data_2 MultiIndex must be named'
                )
        else:
            if data_2.index.name is None:
                raise ValueError('data_2 index must be named')
    else:
        raise TypeError('data_2 must be Series or DataFrame')

    # drop indexes
    if is_multi_1 and is_multi_2:
        if set(data_1.index.names) != set(data_2.index.names):
            raise ValueError(
                f'MultiIndexes for "{data_1.name}" and "{data_2.name}"'
                f' must have the same names'
            )
    elif not is_multi_1 and is_multi_2:
        if not {data_1.index.name}.issubset(data_2.index.names):
            raise ValueError(
                f'Index name for "{data_1.name}" must be one of '
                f'MultiIndex names for "{data_2.name}"'
            )
        # drop redundant indexes for data_2
        for index_name in data_2.index.names:
            if index_name != data_1.index.name:
                data_2.index = data_2.index.droplevel(index_name)
    elif is_multi_1 and not is_multi_2:
        if not {data_2.index.name}.issubset(data_1.index.names):
            raise ValueError(
                f'Index name for "{data_2.name}" must be one of '
                f'MultiIndex names for "{data_1.name}"'
            )
        # drop redundant indexes for data_1
        for index_name in data_1.index.names:
            if index_name != data_2.index.name:
                data_1.index = data_1.index.droplevel(index_name)
        pass
    else:  # not is_multi_1 and not is_multi_2
        if not data_1.index.name == data_2.index.name:
            raise ValueError(
                f'Index names for "{data_1.name}" and "{data_2.name}"'
                f' must be identical'
            )

    # count coincidences
    data = merge(left=data_1, right=data_2, how='outer',
                 left_index=True, right_index=True)
    datas_1: List[Series] = (
        [data_1] if isinstance(data_1, Series)
        else [data_1[col] for col in data_1.columns]
    )
    datas_2: List[Series] = (
        [data_2] if isinstance(data_2, Series)
        else [data_2[col] for col in data_2.columns]
    )
    cp_lists = []
    for d1, d2 in product(datas_1, datas_2):
        d1_name = d1.name if d1.name in data.columns else d1.name + '_x'
        d2_name = d2.name if d2.name in data.columns else d2.name + '_y'
        cp_list = data[[
            d1_name, d2_name
        ]].groupby([d1_name, d2_name]).size().reset_index()
        cp_list.columns = [column_1, column_2, 'count']
        cp_lists.append(cp_list)
    cp_table = pivot_table(
        data=concat(cp_lists),
        index=column_2, columns=column_1,
        values='count'
    ).reindex(
        index=column_2_order, columns=column_1_order
    ).fillna(0)

    return cp_table
