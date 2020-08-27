from typing import Optional, List

from survey.generation.formatting import comma_or
from survey.generation.mixins.name_index_mixin import NameIndexMixin


class Dependency(object):
    """
    Class to place a dependency on whether a question is asked or not.

    """
    def __init__(self, dependency_type: str,
                 independent: str,
                 choices: Optional[List[str]] = None,
                 condition: Optional[str] = None):
        """
        Create a new Dependency.
        Must specify the name of the independent question which will be used to
        test if the dependency is satisfied and either
            (a) a list of choices which will satisfy the dependency if any of
                them are selected, OR
            (b) a string which specifies the dependency in a way the reader will
                understand it.

        :param dependency_type: One of ('show_question', 'show_selected').
                                'show_question` means show if condition is met
                                in `independent`.
                                'show_selected` means only show items selected
                                in `independent`
        :param independent: The question which may or may not satisfy the
                            dependency condition.
        :param choices: Optional list of choices that satisfy the dependency.
        :param condition: Optional text of condition satisfying the dependency.
        """
        dependency_types = ('show_question', 'show_selected')
        if dependency_type not in dependency_types:
            raise ValueError(
                f'Dependency Type must be one of {dependency_types}'
            )
        if dependency_type == 'show_question':
            if choices is None and condition is None:
                raise ValueError(
                    'Must give choice or condition '
                    'for a "show_question" dependency'
                )
            if [choices, condition].count(None) != 1:
                raise ValueError(
                    'Either choice or condition must be None '
                    'for a "show_question" dependency'
                )
        self.dependency_type: str = dependency_type
        self.independent = independent
        self.choices: Optional[List[str]] = choices
        self.condition: Optional[str] = condition

    def to_html(self, parent: Optional[NameIndexMixin] = None):
        """
        Write the Dependency to an html string.

        :param parent: Optional parent container to get the index of the
                       independent question.
        """
        # define question ref string
        question_ref = f'[{self.independent}]'
        if parent is not None:
            index = parent.name_index(self.independent)
            if index is not None:
                question_ref = str(index + 1)
        if self.dependency_type == 'show_question':
            if self.choices is not None:
                str_choices = comma_or(
                    items=self.choices, capitalize=False, quotes=True
                )
                str_out = (
                    f'[ONLY ASK IF RESPONDENT SELECTED {str_choices}'
                    f' in Q{question_ref}]'
                )
            elif self.condition is not None:
                str_out = f'[ONLY ASK IF {self.condition} in Q{question_ref}]'
            else:
                raise ValueError()
        elif self.dependency_type == 'show_selected':
            str_out = f'[ONLY SHOW ITEMS SELECTED IN Q{question_ref}]'
        else:
            raise ValueError()
        return str_out

