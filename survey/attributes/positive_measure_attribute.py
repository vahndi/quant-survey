from typing import Optional

from pandas import Series, cut, qcut

from survey.attributes import SingleCategoryAttribute
from survey.attributes._abstract.respondent_attribute import RespondentAttribute
from survey.mixins.data_mixins import NumericDataMixin
from survey.mixins.data_types.continuous_1d_mixin import Continuous1dMixin
from survey.mixins.data_validation.positive_measure_validation_mixin import \
    PositiveMeasureValidationMixin
from survey.mixins.named import NamedMixin


class PositiveMeasureAttribute(
    NamedMixin,
    NumericDataMixin,
    PositiveMeasureValidationMixin,
    Continuous1dMixin,
    RespondentAttribute
):
    """
    An attribute where the value can be zero or any positive real number.
    """
    def __init__(self, name: str, text: str, data: Optional[Series] = None):
        """
        Create a new Positive Measure attribute.

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

    def to_single_category(
            self, method: str, num_categories: int
    ) -> SingleCategoryAttribute:
        """
        Quantize the data and convert to a SingleCategoryAttribute.

        :param method: Pandas method to slice the data. One of {'cut', 'qcut'}.
        :param num_categories: Number of categories to create.
        """
        if method == 'cut':
            data = cut(self.data, num_categories)
        elif method == 'qcut':
            data = qcut(x=self.data, q=num_categories, duplicates='drop')
        else:
            raise ValueError("method must be one of {'cut', 'qcut'}")
        return SingleCategoryAttribute(
            name=self.name, text=self.text,
            categories=data.cat.categories.to_list(),
            ordered=True, data=data
        )

    def __repr__(self):

        return f"PositiveMeasureAttribute(" \
               f"\n\tname='{self.name}'," \
               f"\n\ttext='{self.text}'" \
               f"\n)"
