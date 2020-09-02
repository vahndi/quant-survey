from itertools import product
from typing import Dict, List, Optional, Any, Union, Tuple, Callable, TypeVar, \
    Type

from survey.compound_types import StringOrStringTuple
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.questions._abstract.question import Question


T = TypeVar('T', bound='SingleTypeQuestionContainerMixin')
Q = TypeVar('Q')


class SingleTypeQuestionContainerMixin(object):
    """
    QuestionContainer containing a single type of question e.g. a group of
    LikertQuestion's
    """
    _item_dict: Dict[str, Question]

    def where(self, **kwargs):
        """
        Return a new QuestionContainerMixin with questions containing only the
        responses for users where the filtering conditions are met.
        See FilterableMixin.where() for further documentation.
        """
        constructor = type(self)
        return constructor(questions={
            name: question.where(**kwargs)
            for name, question in self._item_dict.items()
        })

    @property
    def keys(self) -> List[str]:
        return list(self._item_dict.keys())

    def find_key(self, question) -> Optional[str]:

        for k, q in self._item_dict.items():
            if q.name == question.name:
                return k
        return None

    @classmethod
    def split_question(
            cls: Type[T],
            question: Q,
            split_by: Union[CategoricalMixin, List[CategoricalMixin]]
    ) -> T:
        """
        Create a new QuestionGroup by splitting an existing Question
        by the values of a Categorical question or attribute.
        """
        if not isinstance(split_by, list):
            split_by = [split_by]
        split_by_names = [question.name for question in split_by]
        split_by_categories = [s.category_names for s in split_by]
        questions = {}
        for category_combo in list(product(*split_by_categories)):
            conditions = {
                name: category
                for name, category in zip(split_by_names, category_combo)
            }
            if len(split_by_categories) == 1:
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
