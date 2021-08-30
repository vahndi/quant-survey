from typing import Optional

from pandas import Series

from survey.mixins.data_mixins import NumericDataMixin
from survey.mixins.data_types.continuous_1d_mixin import Continuous1dMixin
from survey.mixins.data_validation.positive_measure_validation_mixin import \
    PositiveMeasureValidationMixin
from survey.mixins.named import NamedMixin
from survey.questions._abstract.question import Question


class PositiveMeasureQuestion(
    NamedMixin,
    NumericDataMixin,
    PositiveMeasureValidationMixin,
    Continuous1dMixin,
    Question
):
    """
    A question where the answer can be zero or any positive real number.
    """
    def __init__(self, name: str, text: str, data: Optional[Series] = None):
        """
        Create a new Positive Measure question.

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

        return (f"PositiveMeasureQuestion("
                f"\n\tname='{self.name}',"
                f"\n\ttext='{self.text}'"
                f"\n)")
