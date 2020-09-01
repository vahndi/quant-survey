from typing import Dict, List, Optional

from survey.mixins.categorical_group_mixin import CategoricalGroupMixin
from survey.mixins.containers.question_container_mixin import \
    QuestionContainerMixin
from survey.mixins.containers.single_type_question_container_mixin import \
    SingleTypeQuestionContainerMixin
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.questions import RankedChoiceQuestion
from survey.utils.type_detection import all_are


class RankedChoiceQuestionGroup(QuestionContainerMixin,
                                SingleTypeQuestionContainerMixin,
                                CategoricalGroupMixin,
                                object):

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

    def question(self, name: str) -> Optional[RankedChoiceQuestion]:
        """
        Return the Question with the given name.

        :param name: Name of the question to return.
        """
        return super().question(name=name)

    def to_list(self) -> List[RankedChoiceQuestion]:
        """
        Return all the Questions asked in the Survey.
        """
        return self._questions

    @staticmethod
    def split_question(
            question: RankedChoiceQuestion,
            split_by: CategoricalMixin
    ) -> 'RankedChoiceQuestionGroup':
        """
        Create a new RankedChoiceQuestionGroup by splitting an existing
        RankedChoiceQuestion by the values of a Categorical question or
        attribute.
        """
        questions = SingleTypeQuestionContainerMixin._split_question(
            question=question,
            split_by=split_by
        )
        return RankedChoiceQuestionGroup(questions=questions)

    @property
    def items(self) -> List[RankedChoiceQuestion]:
        return self._questions

    def __getitem__(self, item) -> RankedChoiceQuestion:
        """
        Return the question with the given key.
        """
        return self._item_dict[item]

    def __setitem__(self, index, value: RankedChoiceQuestion):
        """
        Add a new question to the group.

        :param index: The accessor key for the question.
        :param value: The question.
        """
        if not isinstance(value, RankedChoiceQuestion):
            raise TypeError('Value to set is not a RankedChoiceQuestion')
        self._item_dict[index] = value
        try:
            setattr(self, index, value)
        except:
            print(f'Warning - could not set dynamic property'
                  f' for Question: {index}')
        self._questions.append(value)
