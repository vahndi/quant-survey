from typing import Dict, List, Optional

from survey.mixins.containers.question_container_mixin import \
    QuestionContainerMixin
from survey.mixins.containers.single_type_question_container_mixin import \
    SingleTypeQuestionContainerMixin
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.questions import CountQuestion
from survey.utils.type_detection import all_are


class CountQuestionGroup(QuestionContainerMixin,
                         SingleTypeQuestionContainerMixin,
                         object):

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

    def question(self, name: str) -> Optional[CountQuestion]:
        """
        Return the Question with the given name.

        :param name: Name of the question to return.
        """
        return super().question(name=name)

    def to_list(self) -> List[CountQuestion]:
        """
        Return all the Questions asked in the Survey.
        """
        return self._questions

    @staticmethod
    def from_question(
            question: CountQuestion,
            split_by: CategoricalMixin
    ) -> 'CountQuestionGroup':
        """
        Create a new CountQuestionGroup by splitting an existing CountQuestion
        by the values of a Categorical question or attribute.
        """
        questions = {}
        for category in split_by.category_names:
            condition = {split_by.name: category}
            questions[category] = question.where(**condition)
        return CountQuestionGroup(questions=questions)

    @property
    def items(self) -> List[CountQuestion]:
        return self._questions

    def __getitem__(self, item) -> CountQuestion:
        """
        Return the question with the given key.
        """
        return self._item_dict[item]

    def __setitem__(self, index, value: CountQuestion):
        """
        Add a new question to the group.

        :param index: The accessor key for the question.
        :param value: The question.
        """
        if not isinstance(value, CountQuestion):
            raise TypeError('Value to set is not a CountQuestion')
        self._item_dict[index] = value
        try:
            setattr(self, index, value)
        except:
            print(f'Warning - could not set dynamic property'
                  f' for Question: {index}')
        self._questions.append(value)
