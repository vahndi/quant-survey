from pandas import Series
from typing import List, Union, Optional

from survey.attributes._abstract.respondent_attribute import RespondentAttribute
from survey.mixins.data_mixins import SingleCategoryDataMixin
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.mixins.data_types.single_category_distribution_mixin import \
    SingleCategoryDistributionMixin
from survey.mixins.data_types.single_category_mixin import SingleCategoryMixin
from survey.mixins.data_types.single_category_pt_mixin import \
    SingleCategoryPTMixin
from survey.mixins.data_types.single_category_significance_mixin import \
    SingleCategorySignificanceMixin
from survey.mixins.data_validation.single_category_validation_mixin import \
    SingleCategoryValidationMixin
from survey.mixins.named import NamedMixin


class SingleCategoryAttribute(
    NamedMixin,
    SingleCategoryDataMixin,
    CategoricalMixin,
    SingleCategoryMixin,
    SingleCategorySignificanceMixin,
    SingleCategoryDistributionMixin,
    SingleCategoryValidationMixin,
    SingleCategoryPTMixin,
    RespondentAttribute
):
    """
    A Categorical Attribute with only one value per Respondent.
    """
    def __init__(self, name: str, text: str,
                 categories: List[str], ordered: bool,
                 data: Optional[Series] = None):

        self._set_name_and_text(name, text)
        self._set_categories(categories)
        if data is not None:
            data = data.astype('category')
        self.data = data
        self._ordered = ordered

    def _validate_data(self, data: Series):
        pass

    def where(self, **kwargs) -> 'SingleCategoryAttribute':
        """
        Return a copy of the question with only the data where the survey
        matches the given arguments. e.g. to filter down to Males who answered
        'Yes' to 'q1', use question.where(gender='Male', q1='Yes')

        See FilterableMixin.where() for further documentation.
        """
        return super().where(**kwargs)

    def drop(self, item: Union[str, List[str]]) -> 'SingleCategoryAttribute':
        """
        Return a new SingleCategoryAttribute without a subset of the items in
        the categories.

        :param item: Item or items to use to filter the data.
        """
        if isinstance(item, str):
            categories = [item]
        else:
            categories = item
        if not set(categories).issubset(self.category_names):
            raise ValueError('Items to drop must be subset of categories.')
        new_data = self._data.loc[~self._data.isin(categories)]
        return SingleCategoryAttribute(
            name=self.name, text=self.text,
            categories=[c for c in self._categories if c not in categories],
            ordered=self._ordered,
            data=new_data
        )

    def __getitem__(
            self, item: Union[str, List[str]]
    ) -> 'SingleCategoryAttribute':
        """
        Return a new SingleCategoryAttribute with a subset of the items in the
        categories.

        :param item: Item or items to use to filter the data.
        """
        if isinstance(item, str):
            categories = [item]
        else:
            categories = item
        if not set(categories).issubset(self.category_names):
            raise ValueError('Items to get must be subset of categories.')
        new_data = self._data.loc[self._data.isin(categories)]
        return SingleCategoryAttribute(
            name=self.name, text=self.text,
            categories=[c for c in self._categories if c in categories],
            ordered=self._ordered,
            data=new_data
        )

    def __repr__(self):

        values = ', '.join(f"'{value}'" for value in self.category_names)

        return (
            f"SingleCategoryAttribute("
            f"\n\tname='{self.name}',"
            f"\n\tvalues=[{values}]"
            f"\n)"
        )

