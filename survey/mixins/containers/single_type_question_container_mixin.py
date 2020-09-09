from copy import copy
from itertools import product
from typing import Dict, List, Optional, Union, Callable, TypeVar, Type, \
    ClassVar, Generic

from pandas import notnull, Series, DataFrame

from survey.compound_types import StringOrStringTuple
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.mixins.data_types.discrete_1d_mixin import Discrete1dMixin
from survey.questions._abstract.question import Question


T = TypeVar('T', bound='SingleTypeQuestionContainerMixin')
Q = TypeVar('Q', bound=Question)


class SingleTypeQuestionContainerMixin(Generic[Q]):
    """
    QuestionContainer containing a single type of question e.g. a group of
    LikertQuestion's
    """
    Q: ClassVar[Callable]
    _item_dict: Dict[str, Q]
    _questions: List[Q]
    data: DataFrame

    @property
    def item_dict(self: T) -> Dict[str, Q]:
        return self._item_dict

    def question(self, name: str) -> Optional[Q]:
        """
        Return the Question with the given name.

        :param name: Name of the question to return.
        """
        try:
            return [q for q in self._questions if q.name == name][0]
        except IndexError:
            return None

    @property
    def items(self) -> List[Q]:
        return self._questions

    def to_list(self) -> List[Q]:
        """
        Return all the Questions asked in the Survey.
        """
        return self._questions

    def find_key(self, question: Q) -> Optional[str]:
        """
        Find the key for the given question, if it is contained in the Group.
        """
        for k, q in self._item_dict.items():
            if q.name == question.name:
                return k
        return None

    def merge(self, name: Optional[str] = '', **kwargs) -> Q:
        """
        Return a new Question combining all the responses of the different
        questions in the group.
        N.B. assumes that there is a maximum of one response across all
        questions for each respondent.

        :param name: The name for the new merged Question.
        :param kwargs: Attribute values to override in the new merged Question.
        """
        if len(set([type(q) for q in self._questions])) != 1:
            raise TypeError(
                'Questions must all be of the same type to merge answers'
            )
        if self.data.notnull().sum(axis=1).max() > 1:
            raise ValueError(
                'Can only merge when there is a max of one response '
                'across all questions per respondent'
            )
        data = self.data.loc[self.data.notnull().sum(axis=1) == 1]
        new_data = [row.loc[notnull(row)].iloc[0] for _, row in data.iterrows()]
        new_question = copy(self._questions[0])
        new_question.name = name
        new_question._data = Series(data=new_data, name=name)
        for kw, arg in kwargs.items():
            setattr(new_question, kw, arg)
        return new_question

    @classmethod
    def split_question(
            cls: Type[T],
            question: Q,
            split_by: Union[CategoricalMixin, Discrete1dMixin,
                            List[CategoricalMixin], List[Discrete1dMixin]]
    ) -> T:
        """
        Create a new QuestionGroup by splitting an existing Question
        by the values of a Categorical or Discrete Question or Attribute.
        """
        if not isinstance(split_by, list):
            split_by = [split_by]
        split_by_names = [question.name for question in split_by]
        split_by_values = [s.unique() for s in split_by]
        questions = {}
        for category_combo in list(product(*split_by_values)):
            conditions = {
                name: category
                for name, category in zip(split_by_names, category_combo)
            }
            if len(split_by_values) == 1:
                questions[category_combo[0]] = question.where(**conditions)
            else:
                questions[tuple(category_combo)] = question.where(**conditions)

        return cls(questions=questions)

    def split_by_key(
            self: T,
            splitter: Callable[[StringOrStringTuple],
                               Optional[StringOrStringTuple]],
            renamer: Optional[
                Callable[[StringOrStringTuple],
                         StringOrStringTuple]
            ] = None
    ) -> Dict[StringOrStringTuple, T]:
        """
        Split the group into a dictionary of new QuestionGroups.

        :param splitter: Callable that takes the key of each question and
                         returns a new key. Each question that returns the
                         same new key will be placed into the same group.
                         This new key will be the key of the group in the
                         returned dict.
        :param renamer: Optional Callable to provide a new name for each key.
        """
        split_dict = {}
        for question_key, question in self._item_dict.items():
            group_key = splitter(question_key)
            if group_key is None:
                continue
            if group_key not in split_dict.keys():
                split_dict[group_key] = {}
            if renamer is not None:
                question_key = renamer(question_key)
            split_dict[group_key][question_key] = question
        return {
            new_key: type(self)(questions=split_dict[new_key])
            for new_key in split_dict.keys()
        }

    def map_keys(
            self: T,
            mapper: Callable[[StringOrStringTuple], StringOrStringTuple]
    ) -> T:
        """
        Return a new QuestionGroup with keys mapped using mapper.

        :param mapper: Callable to map existing keys to new keys.
        """
        return type(self)({
            mapper(key): question
            for key, question in self._item_dict.items()
        })

    def __getitem__(self, item) -> Q:
        """
        Return the question with the given key.
        """
        return self._item_dict[item]

    def __setitem__(self, index, value: Q):
        """
        Add a new question to the group.

        :param index: The accessor key for the question.
        :param value: The question.
        """
        if not isinstance(value, self.Q):
            raise TypeError(f'Value to set is not a {self.Q.__name__}')
        self._item_dict[index] = value
        try:
            setattr(self, index, value)
        except:
            print(f'Warning - could not set dynamic property'
                  f' for Question: {index}')
        self._questions.append(value)
