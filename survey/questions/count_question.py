from typing import Optional

from pandas import Series

from survey.mixins.data_mixins import NumericDataMixin
from survey.mixins.data_types.discrete_1d_mixin import Discrete1dMixin
from survey.mixins.data_validation.count_validation_mixin import \
    CountValidationMixin
from survey.mixins.named import NamedMixin
from survey.questions._abstract.question import Question


class CountQuestion(
    NamedMixin,
    NumericDataMixin,
    CountValidationMixin,
    Discrete1dMixin,
    Question
):
    """
    A question where the answer can be zero or any positive integer.
    """
    def __init__(self, name: str, text: str, data: Optional[Series] = None):
        """
        Create a new Count Question.

        :param name: A pythonic name for the question.
        :param text: The text of the question.
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
            f"CountQuestion(\n"
            f"\tname='{self.name}',\n"
            f"\ttext='{self.text}'\n"
            f")"
        )
