from typing import Dict, List, Optional

from survey.custom_types import NumericalQuestion
from survey.mixins.containers.multi_type_question_container_mixin import \
    MultiTypeQuestionContainerMixin
from survey.mixins.containers.question_container_mixin import \
    QuestionContainerMixin


class NumericalQuestionGroup(
    QuestionContainerMixin,
    MultiTypeQuestionContainerMixin,
    object
):

    def __init__(self, questions: Dict[str, NumericalQuestion] = None):

        self._questions: List[NumericalQuestion] = [
            q for q in questions.values()]
        self._item_dict: Dict[str, NumericalQuestion] = questions
        for property_name, question in questions.items():
            try:
                setattr(self, property_name, question)
            except:
                print(f'Warning - could not set dynamic property'
                      f' for Question: {question}')

    def question(self, name: str) -> Optional[NumericalQuestion]:
        """
        Return the Question with the given name.

        :param name: Name of the question to return.
        """
        return super().question(name=name)

    def to_list(self) -> List[NumericalQuestion]:
        """
        Return all the Questions asked in the Survey.
        """
        return self._questions

    @property
    def items(self) -> List[NumericalQuestion]:
        return self._questions

    def __getitem__(self, item) -> NumericalQuestion:
        """
        Return the question with the given key.
        """
        return self._item_dict[item]
