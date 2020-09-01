from itertools import product
from typing import Dict, List, Optional, Any, Union, Tuple

from survey.questions._abstract.question import Question


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

    @staticmethod
    def split_question(
            question: Any, split_by: Union[Any, List[Any]]
    ) -> Dict[Union[str, Tuple[str, ...]], Any]:
        """
        Create a new QuestionGroup of a given type by splitting an existing
        Question of that type by the values of a Categorical Question or
        Attribute.
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

        return questions
