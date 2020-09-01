from typing import Dict, List, Optional

from survey.mixins.containers.question_container_mixin import \
    QuestionContainerMixin
from survey.mixins.containers.single_type_question_container_mixin import \
    SingleTypeQuestionContainerMixin
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.questions import FreeTextQuestion
from survey.utils.type_detection import all_are


class FreeTextQuestionGroup(QuestionContainerMixin,
                            SingleTypeQuestionContainerMixin,
                            object):

    def __init__(self, questions: Dict[str, FreeTextQuestion] = None):

        if not all_are(questions.values(), FreeTextQuestion):
            raise TypeError('Not all attributes are FreeTextQuestions.')
        self._questions: List[FreeTextQuestion] = [
            q for q in questions.values()]
        self._item_dict: Dict[str, FreeTextQuestion] = questions
        for property_name, question in questions.items():
            try:
                setattr(self, property_name, question)
            except:
                print(f'Warning - could not set dynamic property'
                      f' for Question: {question}')

    def question(self, name: str) -> Optional[FreeTextQuestion]:
        """
        Return the Question with the given name.

        :param name: Name of the question to return.
        """
        return super().question(name=name)

    def to_list(self) -> List[FreeTextQuestion]:
        """
        Return all the Questions asked in the Survey.
        """
        return self._questions

    @staticmethod
    def from_question(
            question: FreeTextQuestion,
            split_by: CategoricalMixin
    ) -> 'FreeTextQuestionGroup':
        """
        Create a new FreeTextQuestionGroup by splitting an existing
        FreeTextQuestion by the values of a Categorical question or attribute.
        """
        questions = {}
        for category in split_by.category_names:
            condition = {split_by.name: category}
            questions[category] = question.where(**condition)
        return FreeTextQuestionGroup(questions=questions)

    @property
    def items(self) -> List[FreeTextQuestion]:
        return self._questions

    def __getitem__(self, item) -> FreeTextQuestion:
        """
        Return the question with the given key.
        """
        return self._item_dict[item]

    def __setitem__(self, index, value: FreeTextQuestion):
        """
        Add a new question to the group.

        :param index: The accessor key for the question.
        :param value: The question.
        """
        if not isinstance(value, FreeTextQuestion):
            raise TypeError('Value to set is not a FreeTextQuestion')
        self._item_dict[index] = value
        try:
            setattr(self, index, value)
        except:
            print(f'Warning - could not set dynamic property'
                  f' for Question: {index}')
        self._questions.append(value)
