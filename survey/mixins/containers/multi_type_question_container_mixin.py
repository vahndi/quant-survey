from typing import Dict, Optional, List

from survey.questions import Question


class MultiTypeQuestionContainerMixin(object):

    _questions: List[Question]
    _item_dict: Dict[str, Question]

    @property
    def item_dict(self) -> Dict[str, Question]:
        return self._item_dict

    def question(self, name: str) -> Optional[Question]:
        """
        Return the Question with the given name.

        :param name: Name of the question to return.
        """
        try:
            return [q for q in self._questions if q.name == name][0]
        except IndexError:
            return None

    @property
    def items(self) -> List[Question]:
        return self._questions

    def to_list(self) -> List[Question]:
        """
        Return all the Questions asked in the Survey.
        """
        return self._questions
