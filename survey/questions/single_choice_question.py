from pandas import Series, concat
from typing import List, Union, Optional

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
from survey.questions._abstract.question import Question


class SingleChoiceQuestion(
    NamedMixin,
    SingleCategoryDataMixin,
    CategoricalMixin,
    SingleCategoryMixin,
    SingleCategoryDistributionMixin,
    SingleCategorySignificanceMixin,
    SingleCategoryValidationMixin,
    SingleCategoryPTMixin,
    Question
):
    """
    A Question where the Respondent can choose just one option from at least two
    choices.
    """
    def __init__(self, name: str, text: str,
                 categories: List[str], ordered: bool,
                 data: Optional[Series] = None):
        """
        Create a new Single Choice question.

        :param name: A pythonic name for the question.
        :param text: The text asked in the question.
        :param categories: The list of possible choices.
        :param ordered: Whether the choices passed are ordered (low to high).
        :param data: Optional pandas Series of responses.
        """
        self._set_name_and_text(name, text)
        self._set_categories(categories)
        if data is not None:
            data = data.astype('category')
        self.data = data
        self._ordered = ordered

    def _validate_data(self, data: Series):

        errors = []
        for unique_val in data.dropna().unique():
            if unique_val not in self._categories:
                errors.append(f'"{unique_val}" is not in categories.')
        if errors:
            raise ValueError('\n'.join(errors))

    def drop(self, item: Union[str, List[str]]) -> 'SingleChoiceQuestion':
        """
        Return a new SingleChoiceQuestion without a subset of the items in the
        categories.

        :param item: Item or items to use to filter the data.
        """
        if isinstance(item, str):
            categories = [item]
        else:
            categories = item
        if not set(categories).issubset(self.category_names):
            raise ValueError('Items to drop must be subset of categories.')
        new_data = self._data.loc[~self._data.isin(categories)]
        return SingleChoiceQuestion(
            name=self.name, text=self.text,
            categories=[c for c in self._categories if c not in categories],
            ordered=self._ordered,
            data=new_data
        )

    def __getitem__(
            self, item: Union[str, List[str]]
    ) -> 'SingleChoiceQuestion':
        """
        Return a new SingleChoiceQuestion with a subset of the items in the
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
        return SingleChoiceQuestion(
            name=self.name, text=self.text,
            categories=[c for c in self._categories if c in categories],
            ordered=self._ordered,
            data=new_data
        )

    def __repr__(self):

        choices = ', '.join(f"'{choice}'" for choice in self._categories)
        return (
            f"SingleChoiceQuestion(\n"
            f"\tname='{self.name}',\n"
            f"\ttext='{self.text}'\n"
            f"\tchoices=[{choices}],\n"
            f"\tordered={self._ordered}\n"
            f")"
        )

    def merge_with(
            self, other: 'SingleChoiceQuestion', **kwargs
    ) -> 'SingleChoiceQuestion':
        """
        Merge the answers to this question with the other.

        :param other: The other question to merge answers with.
        :param kwargs: Initialization parameters for new question.
                       Use self values if not given.
        """
        if self.categories != other.categories:
            raise ValueError('Categories must be identical to merge questions.')
        kwargs['data'] = self._get_merge_data(other)
        kwargs = self._update_init_dict(
            kwargs, 'name', 'text', 'categories', 'ordered'
        )
        new_question = SingleChoiceQuestion(**kwargs)
        new_question.survey = self.survey
        return new_question

    def stack(self, other: 'SingleChoiceQuestion',
              name: Optional[str] = None,
              text: Optional[str] = None) -> 'SingleChoiceQuestion':

        if self.data.index.names != other.data.index.names:
            raise ValueError('Indexes must have the same names.')
        if set(self.categories) != set(other.categories):
            raise ValueError('Questions must have the same categories.')
        new_data = concat([self.data, other.data])
        new_question = SingleChoiceQuestion(
            name=name or self.name, text=text or self.text,
            categories=self.categories,
            ordered=self._ordered,
            data=new_data
        )
        new_question.survey = self.survey
        return new_question
