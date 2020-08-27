from typing import Optional, List

from survey.generation.formatting import comma_or


class Termination(object):
    """
    Class to represent when a survey should be terminated for a given
    respondent.
    """
    def __init__(self, choices: Optional[List[str]] = None,
                 termination_type: Optional[str] = None,
                 value: Optional[str] = None,
                 otherwise: str = None):
        """
        Create a new Termination.

        :param choices: List of choices to use if the termination condition is
                        a selection.
        :param termination_type: Options for the type of Termination.
            'any' terminates where any of `choices` are selected.
            'except' terminates where any except `choices` are selected.
            'none' terminates when none of `choices` are selected.
            'only' terminates when only `choices` are selected.
            'single' terminates when `choices` is selected.
            'less_than' terminates when `choices[0]` <  `value`.
            'greater_than' terminates when `choices[0]` >  `value`.
            'greater_than' terminates when `choices[0]` ==  `value`.
        :param value: Value to be used when termination_type is a comparison.
        :param otherwise: String to specify what to do if the termination
                          condition is not met.
        """
        assert termination_type in ('any', 'except', 'none', 'only', 'single',
                                    'less_than', 'greater_than', 'equals')
        self.choices: List[str] = choices or []
        self.termination_type: str = (
            termination_type if isinstance(termination_type, str) else None
        )
        if termination_type in ('only', 'single'):
            if len(self.choices) != 1:
                raise ValueError('1 choice should be given for an '
                                 '"only" or "single" termination.')
        elif termination_type == 'except':
            if len(self.choices) == 0:
                raise ValueError('At least 1 choice must be given'
                                 ' for an "except" termination.')
        elif termination_type in ('any', 'none'):
            if len(self.choices) < 2:
                raise ValueError('At least 2 choices should be given'
                                 ' for an "any" or "none" termination.')
        elif termination_type in ('less_than', 'greater_than', 'equals'):
            if value is None:
                raise ValueError(
                    'value must be given for a comparison termination.'
                )
            if self.choices is not None and len(self.choices) > 1:
                raise ValueError('Can only give 0 or 1 choices'
                                 ' for a comparison termination')
        self.otherwise = otherwise
        self.value: Optional[str] = value

    def to_html(self) -> str:
        """
        Write the termination condition to an html string.
        """
        comparator_symbols = {
            'less_than': '<',
            'greater_than': '>',
            'equals': '=',
        }
        if len(self.choices) > 0:
            str_choices = comma_or(self.choices, capitalize=True, quotes=True)
        if self.otherwise is not None:
            str_otherwise = f' OTHERWISE {self.otherwise}'
        else:
            str_otherwise = ''
        if self.termination_type == 'any':
            return f'[TERMINATE IF ANY OF {str_choices} ' \
                   f'ARE SELECTED{str_otherwise}]'
        elif self.termination_type == 'except':
            return f'[TERMINATE EXCEPT IF {str_choices} ' \
                   f'IS SELECTED{str_otherwise}]'
        elif self.termination_type == 'none':
            return f'[TERMINATE IF NONE OF {str_choices} ' \
                   f'ARE SELECTED{str_otherwise}]'
        elif self.termination_type == 'only':
            return f'[TERMINATE IF ONLY {str_choices} ' \
                   f'IS SELECTED{str_otherwise}]'
        elif self.termination_type == 'single':
            return f'[TERMINATE IF {str_choices} ' \
                   f'IS SELECTED{str_otherwise}]'
        elif self.termination_type in comparator_symbols.keys():
            if len(self.choices) == 0:
                return f'[TERMINATE IF ' \
                       f'{comparator_symbols[self.termination_type]} ' \
                       f'{self.value}{str_otherwise}]'
            elif len(self.choices) == 1:
                return f'[TERMINATE IF "{self.choices[0]}" ' \
                       f'{comparator_symbols[self.termination_type]} ' \
                       f'{self.value}{str_otherwise}]'
        else:
            raise ValueError(f'Invalid Option: {self.termination_type}')
