from typing import Dict, List, Optional

from survey.questions._abstract.question import Question


class SingleTypeQuestionContainerMixin(object):

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
