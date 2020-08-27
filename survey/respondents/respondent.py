from typing import List

from survey.compound_types import GroupPairs
from survey.utils.processing import get_group_pairs


class Respondent(object):
    """
    Class to represent a Survey Respondent.
    """
    def __init__(self, respondent_id, attributes: dict):
        """
        Create a new Respondent instance.

        :param respondent_id: Unique identifier for the Respondent.
        :param attributes: Dictionary mapping attributes of the Respondent
                           to their values.
        """
        self._respondent_id = respondent_id
        self._attributes = attributes

    def __getitem__(self, attribute_name: str):
        """
        Return the value of an attribute of the Respondent.

        :param attribute_name: The name of the attribute whose value to return.
        """
        if attribute_name in self._attributes.keys():
            return self._attributes[attribute_name]
        else:
            raise KeyError

    @property
    def respondent_id(self):
        return self._respondent_id

    @property
    def attribute_names(self) -> List[str]:
        """
        Return a list of all the attribute names the Respondent has.
        """
        return sorted(self._attributes.keys())

    def attribute_group_pairs(self) -> GroupPairs:
        """
        Return all pairs of groups of attribute names
        e.g. (a, [b, c]), ([a, b], c), ([a, c], b)
        """
        return get_group_pairs(
            items=self.attribute_names,
            ordered=False, include_empty=False
        )

    def __repr__(self):

        return f'Respondent(id={self._respondent_id})'
