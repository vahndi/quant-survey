from typing import Dict, List

from survey.mixins.containers.question_container_mixin import \
    QuestionContainerMixin
from survey.mixins.containers.single_type_question_container_mixin import \
    SingleTypeQuestionContainerMixin
from survey.questions import FreeTextQuestion
from survey.utils.type_detection import all_are


class FreeTextQuestionGroup(
    QuestionContainerMixin,
    SingleTypeQuestionContainerMixin[FreeTextQuestion],
    object
):

    def __init__(self, questions: Dict[str, FreeTextQuestion] = None):

        if not all_are(questions.values(), FreeTextQuestion):
            raise TypeError('Not all attributes are FreeTextQuestions.')
        self._questions: List[FreeTextQuestion] = [q for q in questions.values()]
        self._item_dict: Dict[str, FreeTextQuestion] = questions
        for property_name, question in questions.items():
            try:
                setattr(self, property_name, question)
            except:
                print(f'Warning - could not set dynamic property'
                      f' for Question: {question}')

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
