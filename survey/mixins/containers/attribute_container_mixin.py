from copy import copy
from pandas import DataFrame, concat, notnull, Series
from typing import List, Optional

from survey.attributes import RespondentAttribute


class AttributeContainerMixin(object):

    _attributes: List[RespondentAttribute]

    @property
    def data(self) -> DataFrame:
        """
        Return a DataFrame combining data from all the questions in the group.
        """
        return concat([a.data for a in self._attributes], axis=1)

    def attribute(self, name: str) -> Optional[RespondentAttribute]:
        """
        Return the Attribute with the given name.

        :param name: Name of the attribute to return.
        """
        try:
            return [a for a in self._attributes if a.name == name][0]
        except IndexError:
            return None

    def to_list(self) -> List[RespondentAttribute]:
        """
        Return all the Attributes asked in the Survey.
        """
        return self._attributes

    def merge(self, name: Optional[str] = '', **kwargs) -> RespondentAttribute:
        """
        Return a new Question combining all the responses of the different
        questions in the group.
        N.B. assumes that there is a maximum of one response across all
        questions for each respondent.

        :param name: The name for the new merged Question.
        :param kwargs: Attribute values to override in the new merged Question.
        """
        if len(set([type(q) for q in self._attributes])) != 1:
            raise TypeError(
                'Questions must all be of the same type to merge answers.'
            )
        if self.data.notnull().sum(axis=1).max() > 1:
            raise ValueError(
                'Can only merge when there is a max of one response '
                'across all questions per respondent.'
            )
        data = self.data.loc[self.data.notnull().sum(axis=1) == 1]
        new_data = [row.loc[notnull(row)].iloc[0] for _, row in data.iterrows()]
        new_attribute = copy(self._attributes[0])
        new_attribute.name = name
        new_attribute._data = Series(data=new_data, name=name)
        for kw, arg in kwargs.items():
            setattr(new_attribute, kw, arg)
        return new_attribute
