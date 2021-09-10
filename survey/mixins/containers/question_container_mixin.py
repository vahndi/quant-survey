from typing import Dict, List, TypeVar

from pandas import concat, DataFrame

from survey.questions._abstract.question import Question


T = TypeVar('T', bound='QuestionContainerMixin')


class QuestionContainerMixin(object):

    _questions: List[Question]
    _item_dict: Dict[str, Question]

    @property
    def data(self) -> DataFrame:
        """
        Return a DataFrame combining data from all the questions in the group.
        """
        return concat([q.data for q in self._questions], axis=1)

    def where(self: T, **kwargs) -> T:
        """
        Return a new QuestionContainerMixin with questions containing only the
        responses for users where the filtering conditions are met.
        See FilterableMixin.where() for further documentation.
        """
        return type(self)(questions={
            name: question.where(**kwargs)
            for name, question in self._item_dict.items()
        })

    def to_list(self) -> List[Question]:
        """
        Return all the Questions asked in the Survey.
        """
        return self._questions

    @property
    def keys(self) -> List[str]:
        return list(self._item_dict.keys())
