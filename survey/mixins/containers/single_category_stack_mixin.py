from copy import copy
from pandas import concat, Index, MultiIndex, Series
from typing import Optional, Union, List, Dict

from survey.mixins.data_types.single_category_mixin import SingleCategoryMixin


class SingleCategoryStackMixin(object):

    items: List[SingleCategoryMixin]
    _item_dict: Dict[str, SingleCategoryMixin]

    def stack(
            self, name: str,
            drop_na: bool = True,
            name_index: Optional[str] = None,
            key_index: Optional[str] = None,
            number_index: Optional[str] = None,
            number_mappings: Optional[Union[List[str], Dict[int, str]]] = None,
            **kwargs
    ) -> SingleCategoryMixin:
        """
        Stack the responses to each item in the group into a new item.

        :param name: Name for the new item.
        :param drop_na: Whether to drop rows where the respondent was not asked
                        the item.
        :param name_index: Name of a new index column to create with values
                           corresponding to the name of the item the data
                           comes from.
        :param number_index: Name of a new index column to create with values
                             corresponding to the number of the item the data
                             comes from.
        :param key_index: Name of a new index column to create with values
                          corresponding to the item's key in the group.
        :param number_mappings: List of string or dict of ints to strings to
                                convert number index values.
        :param kwargs: Optional new attribute values to override in the new
                       item.
        """
        if name == '':
            raise ValueError('Name cannot be empty.')
        # create index names
        index_names = [self.items[0].data.index.name]
        if name_index is not None:
            index_names.append(name_index)
        if key_index is not None:
            index_names.append(key_index)
        if number_index is not None:
            index_names.append(number_index)

        question_datas = []
        item: SingleCategoryMixin

        for item in self.items:
            # create data
            item_data = item.data
            if drop_na:
                item_data = item_data.dropna()
            # create index
            index_list = item_data.index.to_list()
            if name_index is not None:
                name_list = [item.name] * len(item_data)
            else:
                name_list = None
            if key_index is not None:
                key_list = [
                    [k for k in self._item_dict.keys()
                     if self._item_dict[k] is item][0]
                ] * len(item_data)
            else:
                key_list = None
            if number_index is not None:
                if number_mappings is None:
                    number_list = [self.items.index(item)] * len(item_data)
                else:
                    number_list = [
                        number_mappings[self.items.index(item)]
                    ] * len(item_data)
            else:
                number_list = None
            if name_list is None and key_list is None and number_list is None:
                item_data.index = Index(data=index_list, name=index_names[0])
            else:
                index_tuples = list(
                    zip(*[ix_list
                          for ix_list in [index_list, name_list,
                                          key_list, number_list]
                          if ix_list is not None])
                )
                item_data.index = MultiIndex.from_tuples(
                    tuples=index_tuples, names=index_names
                )
            question_datas.append(item_data)
        new_data = concat(question_datas, axis=0)
        new_data = Series(data=new_data, name=name, index=new_data.index)

        # copy question
        new_question = copy(self.items[0])
        new_question.name = name
        new_question._data = new_data

        for kw, arg in kwargs.items():
            setattr(new_question, kw, arg)

        return new_question
