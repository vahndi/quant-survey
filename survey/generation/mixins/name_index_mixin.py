from typing import List, Optional


class NameIndexMixin(object):
    """
    Mixin to return the index of a question by name.
    """
    question_names: List[str]

    def name_index(self, question_name: str) -> Optional[int]:
        names = self.question_names
        if question_name not in names:
            return None
        return names.index(question_name)
