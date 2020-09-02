from typing import Dict, List, Optional

from survey.custom_types import CategoricalQuestion
from survey.mixins.categorical_group_mixin import CategoricalGroupMixin
from survey.mixins.containers.multi_type_question_container_mixin import \
    MultiTypeQuestionContainerMixin
from survey.mixins.containers.question_container_mixin import \
    QuestionContainerMixin


class CategoricalQuestionGroup(
    QuestionContainerMixin,
    MultiTypeQuestionContainerMixin,
    CategoricalGroupMixin,
    object
):

    def __init__(self, questions: Dict[str, CategoricalQuestion] = None):

        self._questions: List[CategoricalQuestion] = [
            q for q in questions.values()]
        self._set_categories()
        self._item_dict: Dict[str, CategoricalQuestion] = questions
        for property_name, question in questions.items():
            try:
                setattr(self, property_name, question)
            except:
                print(f'Warning - could not set dynamic property'
                      f' for Question: {question}')

    def question(self, name: str) -> Optional[CategoricalQuestion]:
        """
        Return the Question with the given name.

        :param name: Name of the question to return.
        """
        return super().question(name=name)

    def to_list(self) -> List[CategoricalQuestion]:
        """
        Return all the Questions asked in the Survey.
        """
        return self._questions

    @property
    def items(self) -> List[CategoricalQuestion]:
        return self._questions

    def __getitem__(self, item) -> CategoricalQuestion:
        """
        Return the question with the given key.
        """
        return self._item_dict[item]
