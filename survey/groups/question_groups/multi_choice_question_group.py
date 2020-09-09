from copy import copy
from typing import Dict, List, Optional, Union

from numpy import nan
from pandas import concat, Index, MultiIndex, DataFrame, Series

from survey.constants import CATEGORY_SPLITTER
from survey.mixins.categorical_group_mixin import CategoricalGroupMixin
from survey.mixins.containers.question_container_mixin import \
    QuestionContainerMixin
from survey.mixins.containers.single_type_question_container_mixin import \
    SingleTypeQuestionContainerMixin
from survey.questions import MultiChoiceQuestion
from survey.utils.type_detection import all_are


class MultiChoiceQuestionGroup(
    QuestionContainerMixin,
    SingleTypeQuestionContainerMixin[MultiChoiceQuestion],
    CategoricalGroupMixin,
    object
):

    Q = MultiChoiceQuestion

    def __init__(self, questions: Dict[str, MultiChoiceQuestion] = None):

        if not all_are(questions.values(), MultiChoiceQuestion):
            raise TypeError('Not all attributes are MultiChoiceQuestions.')
        self._questions: List[MultiChoiceQuestion] = [q for q in questions.values()]
        self._set_categories()
        self._item_dict: Dict[str, MultiChoiceQuestion] = questions
        for property_name, question in questions.items():
            try:
                setattr(self, property_name, question)
            except:
                print(f'Warning - could not set dynamic property'
                      f' for Question: {question}')

    def stack(self, name: str,
              drop_na: bool = True,
              null_category: Optional[str] = None,
              name_index: Optional[str] = None,
              key_index: Optional[str] = None,
              number_index: Optional[str] = None,
              **kwargs):
        """
        Stack the responses to each question in the group into a new question.

        :param name: Name for the new question.
        :param drop_na: For MultiChoiceQuestions, whether to drop rows where the
                        respondent was not asked the question.
        :param null_category: For MultiChoiceQuestions, optional response to
                              exclude from the new question group.
        :param name_index: Name of a new index column to create with values
                           corresponding to the name of the question the data
                           comes from.
        :param key_index: Name of a new index column to create with values
                          corresponding to the question's key in the group.
        :param number_index: Name of a new index column to create with values
                             corresponding to the number of the question the
                             data comes from.
        :param kwargs: Optional new attribute values to override in the new
                       question.
        """
        if name == '':
            raise ValueError('Name cannot be empty.')
        # create index names
        index_names = [self._questions[0].data.index.name]
        if name_index is not None:
            index_names.append(name_index)
        if key_index is not None:
            index_names.append(key_index)
        if number_index is not None:
            index_names.append(number_index)

        question_datas = []
        question: MultiChoiceQuestion

        for question in self._questions:
            # create data
            question_data = question.make_features(
                naming='{{choice}}', drop_na=drop_na,
                null_category=null_category
            )
            # create index
            index_list = question_data.index.to_list()
            if name_index is not None:
                name_list = [question.name] * len(question_data)
            else:
                name_list = None
            if key_index is not None:
                key_list = [
                    [k for k in self._item_dict.keys()
                     if self._item_dict[k] == question][0]
                ] * len(question_data)
            else:
                key_list = None
            if number_index is not None:
                number_list = [
                    self._questions.index(question)
                ] * len(question_data)
            else:
                number_list = None
            if name_list is None and key_list is None and number_list is None:
                question_data.index = Index(data=index_list,
                                            name=index_names[0])
            else:
                index_tuples = list(zip(*[
                    ix_list for ix_list in [index_list, name_list,
                                            key_list, number_list]
                    if ix_list is not None
                ]))
                question_data.index = MultiIndex.from_tuples(
                    tuples=index_tuples, names=index_names
                )
            question_datas.append(question_data)
        new_data = concat(question_datas, axis=0)
        new_data = DataFrame({
            column: column_data.replace({1: column, 0: ''})
            for column, column_data in new_data.iteritems()
        })
        new_data = Series(
            data=[
                CATEGORY_SPLITTER.join(row.replace('', nan).dropna().to_list())
                for _, row in new_data.iterrows()
            ],
            index=new_data.index, name=name
        )

        # copy question
        new_question = copy(self._questions[0])
        new_question.name = name
        new_question._data = new_data
        if isinstance(new_question, MultiChoiceQuestion):
            if null_category is not None:
                new_question._categories = [
                    c for c in new_question._categories
                    if c != null_category
                ]
        for kw, arg in kwargs.items():
            setattr(new_question, kw, arg)
        return new_question

    def count(self, by: str = 'key',
              values: Optional[Union[str, List[str]]] = None,
              how: Optional[str] = 'any',
              name_map: Optional[Dict[str, str]] = None):
        """
        Count the number of matching responses for each question in the group.

        :param by: What to use as the index for the returned counts.
                   One of ['key', 'question'].
        :param values: A response value or list of values to match.
                       Leave as None to count all responses.
        :param how: Use 'any' to count every respondent who selects any of the
                    values, 'all' to count only those who select all values.
        :param name_map: Optional dict to replace keys or question names with
                         new names.
        """
        counts = []
        if by == 'key':
            for key, question in self._item_dict.items():
                counts.append({
                    'name': name_map[key] if name_map else key,
                    'count': question.count(values, how)
                })
        elif by == 'question':
            for question in self._questions:
                counts.append({
                    'name': (
                        name_map[question.name] if name_map else question.name
                    ),
                    'count': question.count(values, how)
                })
        else:
            raise ValueError("'by' must be one of ['key', 'question']")

        return DataFrame(counts).set_index('name')['count']

    def __gt__(self, other: 'MultiChoiceQuestionGroup') -> DataFrame:
        """
        Find the probability that each response is more likely to be given in
        group 1 than group 2 for each pair of questions in group 1 and group 2.
        """
        results = {}
        for key in self._item_dict.keys():
            results[key] = self[key] > other[key]
        return DataFrame(results)

    def __lt__(self, other: 'MultiChoiceQuestionGroup') -> DataFrame:
        """
        Find the probability that each response is less likely to be given in
        group 1 than group 2 for each pair of questions in group 1 and group 2.
        """
        return other.__gt__(self)

    def merge_with(
            self, other: 'MultiChoiceQuestionGroup'
    ) -> 'MultiChoiceQuestionGroup':
        """
        Merge the questions in this group with those in the other.

        :param other: The other group to merge questions with.
        """
        if set(self.keys) != set(other.keys):
            raise KeyError(
                'Keys must be identical to merge MultiChoiceQuestionGroups'
            )
        return MultiChoiceQuestionGroup({
            k: self[k].merge_with(other[k])
            for k in self.keys
        })
