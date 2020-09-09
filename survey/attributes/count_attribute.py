from pandas import Series
from typing import Optional

from survey.mixins.data import DataMixin
from survey.mixins.data_types.discrete_1d_mixin import Discrete1dMixin
from survey.mixins.data_validation.count_validation_mixin import \
    CountValidationMixin
from survey.mixins.named import NamedMixin
from survey.attributes._abstract.respondent_attribute import RespondentAttribute


class CountAttribute(
    NamedMixin,
    DataMixin,
    CountValidationMixin,
    Discrete1dMixin,
    RespondentAttribute
):
    """
    An attribute where the value can be zero or any positive integer.
    """
    def __init__(self, name: str, text: str, data: Optional[Series] = None):
        """
        Create a new Count Attribute.

        :param name: A pythonic name for the attribute.
        :param text: The text of the attribute.
        :param data: Optional pandas Series of responses.
        """
        self._set_name_and_text(name, text)
        self._set_data(data)

    def __repr__(self):

        return (
            f"CountAttribute(\n\tname='{self.name}',\n\ttext='{self.text}'\n)"
        )
