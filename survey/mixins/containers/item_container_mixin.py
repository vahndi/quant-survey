from pandas import DataFrame
from typing import List, Optional, Union, Tuple

from survey.attributes import RespondentAttribute, SingleCategoryAttribute
from survey.custom_types import CategoricalQuestion, Categorical, Numerical
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.mixins.data_types.numerical_1d_mixin import Numerical1dMixin
from survey.mixins.data_types.textual_mixin import TextualMixin
from survey.questions import FreeTextQuestion, LikertQuestion, MultiChoiceQuestion, SingleChoiceQuestion
from survey.questions._abstract.question import Question


class ItemContainerMixin(object):

    _questions: List[Question]
    _attributes: List[RespondentAttribute]
    _groups: dict
    question_names: List[str]
    attribute_names: List[str]
    _data: DataFrame

    def _find_name(self, item: Union[Question, RespondentAttribute, str]) -> str:
        """
        Find the name of a Question or Attribute that matches the given item.

        :param item: The item to use to find a match for.
        """
        if isinstance(item, Question) or isinstance(item, RespondentAttribute):
            return item.name
        elif isinstance(item, str):
            if item in self._data.columns.tolist():
                return item
            raise ValueError(f'Could not locate item named "{item}"')
        else:
            raise TypeError('Passed item must be instance of '
                            'str, Question or RespondentAttribute.')

    def _find_categorical_name(self, item: Union[Categorical, str]) -> str:
        """
        Find the name of a Categorical that matches the given item.

        :param item: The item to use to find a match for.
        """
        if isinstance(item, CategoricalMixin) and (
            isinstance(item, RespondentAttribute) or isinstance(item, Question)
        ):
            return item.name
        elif isinstance(item, str):
            item_name = item
            if item_name in self._data.columns.tolist():
                item = self._find_item(item_name)
                if isinstance(item, CategoricalMixin):
                    return item_name
                else:
                    raise TypeError(f'Item "{item_name}" is not Categorical')
            else:
                raise ValueError(
                    f'Could not locate Categorical item "{item_name}"'
                )
        else:
            raise TypeError(
                'Passed item must be instance of str or Categorical.'
            )

    def _find_numerical_name(self, item: Union[Numerical, str]) -> str:
        """
        Find the name of a Numerical that matches the given item.

        :param item: The item to use to find a match for.
        """
        if isinstance(item, Numerical1dMixin) and (
            isinstance(item, RespondentAttribute) or isinstance(item, Question)
        ):
            return item.name
        elif isinstance(item, str):
            item_name = item
            if item_name in self._data.columns.tolist():
                item = self._find_item(item_name)
                if isinstance(item, Numerical1dMixin):
                    return item_name
                else:
                    raise TypeError(
                        f'Item named "{item_name}" is not Numerical'
                    )
            else:
                raise ValueError(
                    f'Could not locate Numerical item named "{item_name}"'
                )
        else:
            raise TypeError(
                f'Passed item must be instance of str or Numerical.'
            )

    def _find_textual_name(self, item: Union[TextualMixin, str]) -> str:
        """
        Find the name of a Numerical that matches the given item.

        :param item: The item to use to find a match for.
        """
        if isinstance(item, TextualMixin) and (
            isinstance(item, RespondentAttribute) or isinstance(item, Question)
        ):
            return item.name
        elif isinstance(item, str):
            item_name = item
            if item_name in self._data.columns.tolist():
                item = self._find_item(item_name)
                if isinstance(item, TextualMixin):
                    return item_name
                else:
                    raise TypeError(f'Item named "{item_name}" is not Textual')
            else:
                raise ValueError(
                    f'Could not locate Textual item named "{item_name}"'
                )
        else:
            raise TypeError(f'Passed item must be instance of str or Textual.')

    def _find_item(
            self, item: Union[str, Categorical, Numerical]
    ) -> Union[Question, RespondentAttribute]:
        """
        Find the Question or Attribute with the given name.

        :param item: The name of the item to find.
        """
        if isinstance(item, Question) or isinstance(item, RespondentAttribute):
            item = item.name
        if not isinstance(item, str):
            raise TypeError('Item must be instance of '
                            'str, Categorical or Numerical.')
        for question in self._questions:
            if question.name == item:
                return question
        for attribute in self._attributes:
            if attribute.name == item:
                return attribute
        for group_name, group in self._groups.items():
            if group_name == item:
                return group
        raise ValueError(f'Could not locate item named {item}')

    def _find_categorical_item(self, item: Union[str, Categorical]) -> Categorical:
        """
        Find the Categorical with the given name.

        :param item: The name of the item to find.
        """
        item = self._find_item(item=item)
        if isinstance(item, CategoricalMixin):
            return item
        else:
            raise TypeError(f'Item named "{item.name}" is not Categorical')

    def _find_numerical_item(self, item: str) -> Numerical:
        """
        Find the Numerical with the given name.

        :param item: The name of the item to find.
        """
        item = self._find_item(item=item)
        if isinstance(item, Numerical1dMixin):
            return item
        else:
            raise TypeError(f'Item named "{item.name}" is not Numerical')

    def _find_textual_item(self, item: str) -> TextualMixin:
        """
        Find the Textual with the given name.

        :param item: The name of the item to find.
        """
        item = self._find_item(item=item)
        if isinstance(item, TextualMixin):
            return item
        else:
            raise TypeError(f'Item named "{item.name}" is not Textual')

    def _find_name_and_values(self, item) -> Tuple[str, Optional[List[str]]]:
        """
        Find the name of a question or attribute that matches the given item and its values.

        :param item: The item to use to find a match for.
        """
        if (
                isinstance(item, SingleChoiceQuestion) or
                isinstance(item, MultiChoiceQuestion)
        ):
            found_item = item.name
            item_values = item.category_names
        elif isinstance(item, SingleCategoryAttribute):
            found_item = item.name
            item_values = item.category_names
        elif isinstance(item, LikertQuestion):
            found_item = item.name
            item_values = item.category_names
        elif isinstance(item, FreeTextQuestion):
            found_item = item.name
            item_values = None
        elif isinstance(item, str):
            found_item = item
            if item in self.attribute_names:
                attribute: SingleCategoryAttribute = self.single_category_attribute(item)
                item_values = attribute.category_names
            elif item in self.question_names:
                question: CategoricalQuestion = self.categorical_question(item)
                item_values = question.category_names
            else:
                item_values = self._data[item].dropna().unique().tolist()
        else:
            raise ValueError(f'Could not locate item {item}')

        return found_item, item_values
