from typing import Dict, List, Optional, Union

from pandas import Series, DataFrame

from survey.mixins.categorical_group_mixin import CategoricalGroupMixin
from survey.mixins.containers.question_container_mixin import \
    QuestionContainerMixin
from survey.mixins.containers.single_category_stack_mixin import \
    SingleCategoryStackMixin
from survey.mixins.containers.single_type_question_container_mixin import \
    SingleTypeQuestionContainerMixin
from survey.mixins.single_category_group.single_category_group_comparison_mixin import \
    SingleCategoryGroupComparisonMixin
from survey.mixins.single_category_group.single_category_group_pt_mixin import \
    SingleCategoryGroupPTMixin
from survey.mixins.single_category_group.single_category_group_significance_mixin import \
    SingleCategoryGroupSignificanceMixin
from survey.questions import SingleChoiceQuestion
from survey.utils.type_detection import all_are


class SingleChoiceQuestionGroup(
    QuestionContainerMixin,
    SingleCategoryStackMixin,
    SingleCategoryGroupSignificanceMixin,
    SingleCategoryGroupComparisonMixin,
    SingleCategoryGroupPTMixin,
    SingleTypeQuestionContainerMixin[SingleChoiceQuestion],
    CategoricalGroupMixin,
    object
):

    Q = SingleChoiceQuestion

    def __init__(self, questions: Dict[str, SingleChoiceQuestion] = None):

        if not all_are(questions.values(), SingleChoiceQuestion):
            raise TypeError('Not all attributes are SingleChoiceQuestions.')
        self._questions: List[SingleChoiceQuestion] = [
            q for q in questions.values()
        ]
        self._set_categories()
        self._item_dict: Dict[str, SingleChoiceQuestion] = questions
        for property_name, question in questions.items():
            try:
                setattr(self, property_name, question)
            except:
                print(f'Warning - could not set dynamic property'
                      f' for Question: {question}')

    def count(self) -> int:
        """
        Count the total number of responses in the group.
        """
        return self.counts().sum()

    def counts(self, index: str = 'key',
               values: Optional[Union[str, List[str]]] = None,
               name_map: Optional[Dict[str, str]] = None) -> Series:
        """
        Count the number of matching responses for each question in the group.

        :param index: What to use as the index for the returned counts.
                      One of ['key', 'question'].
        :param values: A response value or list of values to match.
                       Leave as None to count all responses.
        :param name_map: Optional dict to replace keys or question names with
                         new names.
        """
        counts = []
        if index == 'key':
            for key, question in self._item_dict.items():
                counts.append({
                    'name': name_map[key] if name_map else key,
                    'count': question.count(values)
                })
        elif index == 'question':
            for question in self._questions:
                counts.append({
                    'name': (
                        name_map[question.name] if name_map else question.name
                    ),
                    'count': question.count(values)
                })
        else:
            raise ValueError("'by' must be one of ['key', 'question']")

        return DataFrame(counts).set_index('name')['count']

    def merge_with(
            self, other: 'SingleChoiceQuestionGroup'
    ) -> 'SingleChoiceQuestionGroup':
        """
        Merge the questions in this group with those in the other.

        :param other: The other group to merge questions with.
        """
        if set(self.keys) != set(other.keys):
            raise KeyError(
                'Keys must be identical to merge SingleChoiceQuestionGroups'
            )
        return SingleChoiceQuestionGroup({
            k: self[k].merge_with(other[k])
            for k in self.keys
        })
