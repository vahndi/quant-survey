from typing import Optional

from pandas import Series

from survey.attributes._abstract.respondent_attribute import RespondentAttribute
from survey.mixins.data_mixins import NumericDataMixin
from survey.mixins.data_types.discrete_1d_mixin import Discrete1dMixin
from survey.mixins.data_validation.count_validation_mixin import \
    CountValidationMixin
from survey.mixins.named import NamedMixin


class CountAttribute(
    NamedMixin,
    NumericDataMixin,
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
        if data is not None:
            try:
                data = data.astype(int)
            except ValueError:
                data = data.astype(float)
        self.data = data

    def __repr__(self):

        return (
            f"CountAttribute(\n\tname='{self.name}',\n\ttext='{self.text}'\n)"
        )
