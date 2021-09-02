from typing import Optional

from pandas import Series, cut, qcut

from survey.mixins.data_mixins import NumericDataMixin
from survey.mixins.data_types.continuous_1d_mixin import Continuous1dMixin
from survey.mixins.data_validation.positive_measure_validation_mixin import \
    PositiveMeasureValidationMixin
from survey.mixins.named import NamedMixin
from survey.questions.single_choice_question import SingleChoiceQuestion
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

    def to_single_choice(
            self, method: str, num_categories: int
    ) -> SingleChoiceQuestion:
        """
        Quantize the data and convert to a SingleChoiceQuestion.

        :param method: Pandas method to slice the data. One of {'cut', 'qcut'}.
        :param num_categories: Number of categories to create.
        """
        if method == 'cut':
            data = cut(self.data, num_categories)
        elif method == 'qcut':
            data = qcut(self.data, num_categories)
        else:
            raise ValueError("method must be one of {'cut', 'qcut'}")
        return SingleChoiceQuestion(
            name=self.name, text=self.text,
            categories=data.cat.categories.to_list(),
            ordered=True, data=data
        )

    def __repr__(self):

        return (f"PositiveMeasureQuestion("
                f"\n\tname='{self.name}',"
                f"\n\ttext='{self.text}'"
                f"\n)")
