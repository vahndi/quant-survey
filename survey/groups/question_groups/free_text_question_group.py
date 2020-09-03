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

    Q = FreeTextQuestion

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
