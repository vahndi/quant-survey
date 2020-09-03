from typing import Dict, List

from survey.mixins.containers.question_container_mixin import \
    QuestionContainerMixin
from survey.mixins.containers.single_type_question_container_mixin import \
    SingleTypeQuestionContainerMixin
from survey.questions import CountQuestion
from survey.utils.type_detection import all_are


class CountQuestionGroup(
    QuestionContainerMixin,
    SingleTypeQuestionContainerMixin[CountQuestion],
    object
):

    Q = CountQuestion

    def __init__(self, questions: Dict[str, CountQuestion] = None):

        if not all_are(questions.values(), CountQuestion):
            raise TypeError('Not all attributes are CountQuestions.')
        self._questions: List[CountQuestion] = [q for q in questions.values()]
        self._item_dict: Dict[str, CountQuestion] = questions
        for property_name, question in questions.items():
            try:
                setattr(self, property_name, question)
            except:
                print(f'Warning - could not set dynamic property'
                      f' for Question: {question}')
