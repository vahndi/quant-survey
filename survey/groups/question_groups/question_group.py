from collections import OrderedDict
from typing import Dict, Union, List, Iterator, Optional, Set, Any

from pandas import Series

from survey.custom_types import CategoricalQuestion, CategoricalQuestionTypes, \
    NumericalQuestionTypes, NumericalQuestion
from survey.groups.question_groups.categorical_question_group import \
    CategoricalQuestionGroup
from survey.groups.question_groups.count_question_group import \
    CountQuestionGroup
from survey.groups.question_groups.free_text_question_group import \
    FreeTextQuestionGroup
from survey.groups.question_groups.likert_question_group import \
    LikertQuestionGroup
from survey.groups.question_groups.multi_choice_question_group import \
    MultiChoiceQuestionGroup
from survey.groups.question_groups.numerical_question_group import \
    NumericalQuestionGroup
from survey.groups.question_groups.positive_measure_question_group import \
    PositiveMeasureQuestionGroup
from survey.groups.question_groups.ranked_choice_question_group import \
    RankedChoiceQuestionGroup
from survey.groups.question_groups.single_choice_question_group import \
    SingleChoiceQuestionGroup
from survey.mixins.containers.attribute_container_mixin import \
    AttributeContainerMixin
from survey.mixins.containers.item_container_mixin import ItemContainerMixin
from survey.mixins.containers.question_container_mixin import \
    QuestionContainerMixin
from survey.questions import CountQuestion, FreeTextQuestion, LikertQuestion, \
    MultiChoiceQuestion, RankedChoiceQuestion, PositiveMeasureQuestion, \
    SingleChoiceQuestion
from survey.questions._abstract.question import Question
from survey.respondents import Respondent
from survey.utils.type_detection import all_are

SingleTypeQuestionGroups = Union[
    CountQuestionGroup,
    FreeTextQuestionGroup,
    LikertQuestionGroup,
    MultiChoiceQuestionGroup,
    NumericalQuestionGroup,
    PositiveMeasureQuestionGroup,
    RankedChoiceQuestionGroup,
    SingleChoiceQuestionGroup
]

MixedTypeQuestionGroups = Union[
    CategoricalQuestionGroup,
    NumericalQuestionGroup
]


class QuestionGroup(ItemContainerMixin,
                    QuestionContainerMixin,
                    # AttributeContainerMixin,
                    object):

    def __init__(
            self, items: Dict[str, Union[Question, 'QuestionGroup']] = None
    ):

        if items is not None:
            self._questions = [q for q in items.values()
                               if isinstance(q, Question)]
            self._groups = {name: group for name, group in items.items()
                            if isinstance(group, QuestionContainerMixin)}
            self._item_dict: Dict[str, Union[Question, 'QuestionGroup']] = items

            for property_name, question in items.items():
                try:
                    setattr(self, property_name, question)
                except:
                    print(f'Warning - could not set dynamic property for '
                          f'Question: {question}')
        else:
            self._questions = []
            self._groups = {}
            self._item_dict = {}

    @property
    def question_names(self) -> List[str]:
        """
        Return the name of each Question in the Survey.
        """
        return [question.name for question in self._questions]

    @property
    def question_types(self) -> Set[type]:
        """
        Return a list of unique question types in the Survey.
        """
        return set([type(question) for question in self._questions])

    def question_responses(self, question: Union[Question, str],
                           respondents: List[Respondent] = None,
                           drop_na: bool = True) -> Series:
        """
        Return the value of the Response to the given Question
        for each Respondent in the Survey.

        :param question: The question to return responses for.
        :param respondents: Optional list of Respondents to filter responses to.
        :param drop_na: Whether to drop null responses.
        """
        question_name = (
            question.name if isinstance(question, Question)
            else question
        )
        responses = self.data[question_name]
        if respondents is not None:
            responses = responses.loc[[r.respondent_id for r in respondents]]
        if drop_na:
            responses = responses.dropna()

        return responses

    def response(self, question: Union[Question, str],
                 respondent: Union[Respondent, Any]):
        """
        Return the literal response to a question from a given Respondent.

        :param question: Question or name of the question to find response to.
        :param respondent: The Respondent or their id.
        """
        question_name = (
            question.name if isinstance(question, Question)
            else question
        )
        if isinstance(respondent, Respondent):
            respondent_id = respondent.respondent_id
        else:
            respondent_id = respondent
        return self.data.loc[respondent_id, question_name]

    def new_question_group(
            self, names: Union[List[str], Dict[str, str]]
    ) -> Union[SingleTypeQuestionGroups,
               MixedTypeQuestionGroups,
               'QuestionGroup']:
        """
        Return a new QuestionGroup from named items of the Group.

        :param names: Names of items to return in the QuestionGroup or
                      mapping from existing names to new names.
        """
        group_items: Dict[str, Question] = {}
        for name in names:
            item = self._find_item(name)
            if not (isinstance(item, Question) or
                    isinstance(item, QuestionContainerMixin)):
                raise TypeError(
                    f'Item {item} is not a Question or QuestionGroup.')
            if isinstance(names, list):
                group_items[name] = item
            elif isinstance(names, dict):
                group_items[names[name]] = item
            else:
                raise TypeError('names should be List[str] or Dict[str, str]')
        questions = list(group_items.values())
        if all_are(questions, CountQuestion):
            return CountQuestionGroup(group_items)
        elif all_are(questions, FreeTextQuestion):
            return FreeTextQuestionGroup(group_items)
        elif all_are(questions, LikertQuestion):
            return LikertQuestionGroup(group_items)
        elif all_are(questions, MultiChoiceQuestion):
            return MultiChoiceQuestionGroup(group_items)
        elif all_are(questions, PositiveMeasureQuestion):
            return PositiveMeasureQuestionGroup(group_items)
        elif all_are(questions, RankedChoiceQuestion):
            return RankedChoiceQuestionGroup(group_items)
        elif all_are(questions, SingleChoiceQuestion):
            return SingleChoiceQuestionGroup(group_items)
        else:
            return QuestionGroup(items=group_items)

    def create_question_group(
            self, group_name: str,
            item_names: Union[List[str], Dict[str, str]]
    ):
        """
        Add a new QuestionGroup from the named items of the Group to the Group.

        :param group_name: The name for the new group.
        :param item_names: Names of items to return in the QuestionGroup or
                           mapping from existing names to new names.
        """
        group = self.new_question_group(names=item_names)
        self._groups[group_name] = group
        self._item_dict[group_name] = group
        try:
            setattr(self, group_name, group)
        except:
            print(f'Warning - could not set dynamic group for {group}')

    def add_question_group(self,
                           group_name: str,
                           group: 'QuestionGroup'):

        if group_name in self._groups.keys():
            raise ValueError(f'Group {group_name} already exists!')
        self._groups[group_name] = group
        self._item_dict[group_name] = group
        try:
            setattr(self, group_name, group)
        except:
            print(f'Warning - could not set dynamic group for {group}')

    @property
    def question_groups(self) -> Dict[str, 'QuestionGroup']:

        return self._groups

    # region get all questions of a given type

    @property
    def categorical_questions(self) -> CategoricalQuestionGroup:
        """
        Return all Categorical Questions.
        """
        return CategoricalQuestionGroup(OrderedDict([
            (question.name, question) for question in self._questions
            if type(question) in CategoricalQuestionTypes
        ]))

    @property
    def numerical_questions(self) -> NumericalQuestionGroup:
        """
        Return all Numerical Questions.
        """
        return NumericalQuestionGroup(OrderedDict([
            (question.name, question) for question in self._questions
            if type(question) in NumericalQuestionTypes
        ]))

    @property
    def count_questions(self) -> CountQuestionGroup:
        """
        Return all the Count Questions asked in the survey.
        """
        return CountQuestionGroup(OrderedDict([
            (question.name, question) for question in self._questions
            if isinstance(question, CountQuestion)
        ]))

    @property
    def free_text_questions(self) -> FreeTextQuestionGroup:
        """
        Return all the free text Questions asked in the Survey.
        """
        return FreeTextQuestionGroup(OrderedDict([
            (question.name, question) for question in self._questions
            if isinstance(question, FreeTextQuestion)
        ]))

    @property
    def likert_questions(self) -> LikertQuestionGroup:
        """
        Return all the Likert Questions asked in the survey.
        """
        return LikertQuestionGroup(OrderedDict([
            (question.name, question) for question in self._questions
            if isinstance(question, LikertQuestion)
        ]))

    @property
    def multi_choice_questions(self) -> MultiChoiceQuestionGroup:
        """
        Return all the Multi-Choice Questions asked in the Survey.
        """
        return MultiChoiceQuestionGroup(OrderedDict([
            (question.name, question) for question in self._questions
            if isinstance(question, MultiChoiceQuestion)
        ]))

    @property
    def positive_measure_questions(self) -> PositiveMeasureQuestionGroup:
        """
        Return all the Positive Measure Questions asked in the Survey.
        """
        return PositiveMeasureQuestionGroup(OrderedDict([
            (question.name, question) for question in self._questions
            if isinstance(question, PositiveMeasureQuestion)
        ]))

    @property
    def ranked_choice_questions(self) -> RankedChoiceQuestionGroup:
        """
        Return all the Ranked-Choice Questions asked in the Survey.
        """
        return RankedChoiceQuestionGroup(OrderedDict([
            (question.name, question) for question in self._questions
            if isinstance(question, RankedChoiceQuestion)
        ]))

    @property
    def single_choice_questions(self) -> SingleChoiceQuestionGroup:
        """
        Return all the Single-Choice Questions asked in the Survey.
        """
        return SingleChoiceQuestionGroup(OrderedDict([
            (question.name, question) for question in self._questions
            if isinstance(question, SingleChoiceQuestion)
        ]))

    # endregion

    # region get question of a given type by name

    def categorical_question(self, name: str) -> Optional[CategoricalQuestion]:
        """
        Return the Categorical Question with the given name.
        """
        try:
            return self.categorical_questions[name]
        except KeyError:
            return None

    def count_question(self, name: str) -> Optional[CountQuestion]:
        """
        Return the Count Question with the given name.
        """
        try:
            return self.count_questions[name]
        except KeyError:
            return None

    def free_text_question(self, name: str) -> Optional[FreeTextQuestion]:
        """
        Return the FreeText Question with the given name.
        """
        try:
            return self.free_text_questions[name]
        except KeyError:
            return None

    def likert_question(self, name: str) -> Optional[LikertQuestion]:
        """
        Return the Likert Question with the given name.
        """
        try:
            return self.likert_questions[name]
        except KeyError:
            return None

    def multi_choice_question(self, name: str) -> Optional[MultiChoiceQuestion]:
        """
        Return the Multi-Choice Question with the given name.
        """
        try:
            return self.multi_choice_questions[name]
        except KeyError:
            return None

    def numerical_question(self, name: str) -> Optional[NumericalQuestion]:
        """
        Return the Categorical Question with the given name.
        """
        try:
            return self.numerical_questions[name]
        except KeyError:
            return None

    def ranked_choice_question(
            self, name: str
    ) -> Optional[RankedChoiceQuestion]:
        """
        Return the Ranked-Choice Question with the given name.
        """
        try:
            return self.ranked_choice_questions[name]
        except KeyError:
            return None

    def positive_measure_question(
            self, name: str
    ) -> Optional[PositiveMeasureQuestion]:
        """
        Return the Positive Measure Question with the given name.
        """
        try:
            return self.positive_measure_questions[name]
        except KeyError:
            return None

    def single_choice_question(
            self, name: str
    ) -> Optional[SingleChoiceQuestion]:
        """
        Return the Single-Choice Question with the given name.
        """
        try:
            return self.single_choice_questions[name]
        except KeyError:
            return None

    # endregion

    # region question names by type

    @property
    def categorical_question_names(self) -> List[str]:
        """
        Return the name of each Categorical Question in the Survey.
        """
        return [question.name
                for question in self.categorical_questions.to_list()]

    @property
    def count_question_names(self) -> List[str]:
        """
        Return the name of each CountQuestion names in the Survey.
        """
        return [question.name
                for question in self.count_questions.to_list()]

    @property
    def free_text_question_names(self) -> List[str]:
        """
        Return the name of each Categorical Question in the Survey.
        """
        return [question.name
                for question in self.free_text_questions.to_list()]

    @property
    def likert_question_names(self) -> List[str]:
        """
        Return the name of each LikertQuestion in the Survey.
        """
        return [question.name
                for question in self.likert_questions.to_list()]

    @property
    def multi_choice_question_names(self) -> List[str]:
        """
        Return the name of each LikertQuestion in the Survey.
        """
        return [question.name
                for question in self.multi_choice_questions.to_list()]

    @property
    def numerical_question_names(self) -> List[str]:
        """
        Return the name of each Numerical Question in the Survey.
        """
        return [question.name
                for question in self.numerical_questions.to_list()]

    @property
    def positive_measure_question_names(self) -> List[str]:
        """
        Return the name of each PositiveMeasureQuestion in the Survey.
        """
        return [question.name
                for question in self.positive_measure_questions.to_list()]

    @property
    def single_choice_question_names(self) -> List[str]:
        """
        Return the name of each SingleChoiceQuestion in the Survey.
        """
        return [question.name
                for question in self.single_choice_questions.to_list()]

    # endregion

    # region get existing groups of a given type by name

    def categorical_group(
            self, group_name: str
    ) -> Optional[CategoricalQuestionGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name], CategoricalQuestionGroup)
        ):
            return self._groups[group_name]

    def count_group(self, group_name: str) -> Optional[CountQuestionGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name], CountQuestionGroup)
        ):
            return self._groups[group_name]

    def free_text_group(
            self, group_name: str
    ) -> Optional[FreeTextQuestionGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name], FreeTextQuestionGroup)
        ):
            return self._groups[group_name]

    def likert_group(self, group_name: str) -> Optional[LikertQuestionGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name], LikertQuestionGroup)
        ):
            return self._groups[group_name]

    def multi_choice_group(
            self, group_name: str
    ) -> Optional[MultiChoiceQuestionGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name], MultiChoiceQuestionGroup)
        ):
            return self._groups[group_name]

    def numerical_group(
            self, group_name: str
    ) -> Optional[NumericalQuestionGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name], NumericalQuestionGroup)
        ):
            return self._groups[group_name]

    def positive_measure_group(
            self, group_name: str
    ) -> Optional[PositiveMeasureQuestionGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name],
                           PositiveMeasureQuestionGroup)
        ):
            return self._groups[group_name]

    def ranked_choice_group(
            self, group_name: str
    ) -> Optional[RankedChoiceQuestionGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name], RankedChoiceQuestionGroup)
        ):
            return self._groups[group_name]

    def single_choice_group(
            self, group_name: str
    ) -> Optional[SingleChoiceQuestionGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name], SingleChoiceQuestionGroup)
        ):
            return self._groups[group_name]

    # endregion

    def drop(
            self, items: Union[str, List[str]]
    ) -> Union['QuestionGroup',
               SingleTypeQuestionGroups,
               MixedTypeQuestionGroups]:

        if isinstance(items, str):
            items = [items]
        items = OrderedDict([
            (question_name, question)
            for question_name, question in self._item_dict.items()
            if question_name not in items
        ])
        if all_are(items.values(), CountQuestion):
            return CountQuestionGroup(items)
        elif all_are(items.values(), FreeTextQuestion):
            return FreeTextQuestionGroup(items)
        elif all_are(items.values(), LikertQuestion):
            return LikertQuestionGroup(items)
        elif all_are(items.values(), MultiChoiceQuestion):
            return MultiChoiceQuestionGroup(items)
        elif all_are(items.values(), PositiveMeasureQuestion):
            return PositiveMeasureQuestionGroup(items)
        elif all_are(items.values(), RankedChoiceQuestion):
            return RankedChoiceQuestionGroup(items)
        elif all_are(items.values(), SingleChoiceQuestion):
            return SingleChoiceQuestionGroup(items)
        elif all_are(items.values(), CategoricalQuestion):
            return CategoricalQuestionGroup(items)
        elif all_are(items.values(), NumericalQuestion):
            return NumericalQuestionGroup(items)
        else:
            return QuestionGroup(items)

    def where(self, **kwargs) -> 'QuestionGroup':
        """
        Return a new QuestionGroup with questions containing only the responses
        for users where the filtering conditions are met.
        See FilterableMixin.where() for further documentation.
        """
        return QuestionGroup({
            name: group.where(**kwargs)
            for name, group in self._item_dict.items()
        })

    @property
    def _items(self) -> List[Union[Question, 'QuestionGroup']]:

        return [value for value in self._item_dict.values()]

    def __getitem__(self, item):
        """
        Return the question with the given key.
        """
        return self._item_dict[item]

    def __iter__(self) -> Iterator[Union[Question, 'QuestionGroup']]:

        return self._items.__iter__()
