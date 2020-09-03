from typing import Dict, List

from survey.mixins.categorical_group_mixin import CategoricalGroupMixin
from survey.mixins.containers.question_container_mixin import \
    QuestionContainerMixin
from survey.mixins.containers.single_type_question_container_mixin import \
    SingleTypeQuestionContainerMixin
from survey.questions import RankedChoiceQuestion
from survey.utils.type_detection import all_are


class RankedChoiceQuestionGroup(
    QuestionContainerMixin,
    SingleTypeQuestionContainerMixin[RankedChoiceQuestion],
    CategoricalGroupMixin,
    object
):

    Q = RankedChoiceQuestion

    def __init__(self, questions: Dict[str, RankedChoiceQuestion] = None):

        if not all_are(questions.values(), RankedChoiceQuestion):
            raise TypeError('Not all attributes are RankedChoiceQuestions.')
        self._questions: List[RankedChoiceQuestion] = [
            q for q in questions.values()]
        self._set_categories()
        self._item_dict: Dict[str, RankedChoiceQuestion] = questions
        for property_name, question in questions.items():
            try:
                setattr(self, property_name, question)
            except:
                print(f'Warning - could not set dynamic property'
                      f' for Question: {question}')
