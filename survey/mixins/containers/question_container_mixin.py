from copy import copy
from pandas import concat, DataFrame, notnull, Series
from typing import List, Optional

from survey.questions._abstract.question import Question


class QuestionContainerMixin(object):

    _questions: List[Question]

    @property
    def data(self) -> DataFrame:
        """
        Return a DataFrame combining data from all the questions in the group.
        """
        return concat([q.data for q in self._questions], axis=1)

    def question(self, name: str) -> Optional[Question]:
        """
        Return the Question with the given name.

        :param name: Name of the question to return.
        """
        try:
            return [q for q in self._questions if q.name == name][0]
        except IndexError:
            return None

    def to_list(self) -> List[Question]:
        """
        Return all the Questions asked in the Survey.
        """
        return self._questions

    def merge(self, name: Optional[str] = '', **kwargs) -> Question:
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
