from collections import OrderedDict
from pandas import Series, DataFrame, notnull
from typing import Optional, List, Dict

from survey.generation.dependency import Dependency
from survey.generation.formatting import spaces, bold_blue, comma_and, bold_red
from survey.generation.mixins.name_index_mixin import NameIndexMixin
from survey.generation.termination import Termination


class SurveyQuestion(object):
    """
    Class to generate a Survey Question.
    """
    def __init__(self, name: str, text: str,
                 choices: Optional[List[str]] = None,
                 dependencies: Optional[List[Dependency]] = None,
                 assignments: Optional[Dict[str, str]] = None,
                 terminations: Optional[List[Termination]] = None,
                 ask_to: Optional[List[str]] = None,
                 parent: Optional[NameIndexMixin] = None,
                 randomize: bool = False,
                 notes: Optional[List[str]] = None):
        """

        :param name: The shorthand name for the question.
        :param text: The text to ask the respondent.
        :param choices: List of choices for the respondent to select.
        :param dependencies: List of Dependencies to decide whether to
                             show the question.
        :param assignments: Dictionary mapping selected choice to a group to
                            assign the respondent to if they selected it.
        :param terminations: List of conditions to Terminate the survey after
                             this question.
        :param ask_to: List of groups to ask the question to.
        :param parent: Reference to the section the question belongs to.
        :param randomize: Whether to randomize the responses to the question.
        :param notes: Notes on the question for the survey programmers.
        """
        self.name: str = name
        self.text: str = text
        self.choices = []
        if choices is not None:
            for choice in choices:
                if choice.endswith(' '):
                    raise ValueError(f'Choice "{choice}" ends with a space.')
                self.choices.append(choice)
        self.dependencies: Optional[List[Dependency]] = dependencies or []
        self.assignments = assignments or OrderedDict()
        self.terminations = terminations if terminations is not None else []
        self.ask_to: List[str] = ask_to or []
        self.parent: NameIndexMixin = parent
        self.randomize: bool = randomize
        self.notes = notes or []

    @staticmethod
    def from_data(question_data: Series,
                  choices: DataFrame,
                  assignments: Optional[DataFrame] = None,
                  dependencies: Optional[DataFrame] = None,
                  terminations: Optional[DataFrame] = None,
                  ask_to: Optional[List[str]] = None,
                  add_to_name: Optional[str] = None) -> 'SurveyQuestion':
        """
        Create a question from spreadsheet data.

        :param question_data: Series containing question minimum attributes
                              ['name', 'text', 'randomize', 'choices' 'notes']
        :param choices: DataFrame mapping question names to categories with
                        columns ['name', 'category'].
        :param assignments: DataFrame of Assignment values with columns
                            ['assign_to_group',
                            'assign_if_question', 'assign_if_value']
        :param dependencies: DataFrame of Dependency values with columns
                             ['choice', 'dependency_type', 'condition']
        :param terminations: DataFrame of Termination values with columns
                             ['question', 'choices',
                             'termination_type',  'value', 'otherwise']
        :param ask_to: List of groups to ask the question to.
        :param add_to_name: Optional string to append to the question name.
        """
        question_name = question_data['name']
        question = OrderedDict([
            ('name', question_name + (add_to_name if add_to_name else '')),
            ('text', question_data['text']),
            ('randomize',
             True if question_data['randomize'] == True else False),
            ('notes',
             question_data['notes'].split('\n')
             if notnull(question_data['notes'])
             else None)
        ])
        # get choices
        choices_name = question_data['choices']
        use_features = (
            question_data['use_features']
            if 'use_features' in question_data.keys()
            else False
        )
        if notnull(choices_name) and use_features == True:
            raise ValueError(
                f'must give choices or features for "{question_name}", not both'
            )
        if notnull(choices_name):
            choice_list = choices.loc[
                choices['name'] == choices_name, 'category'
            ].tolist()
            if not len(choice_list) > 0:
                raise ValueError(f'no choices listed for name "{choices_name}"')
            question['choices'] = choice_list
        else:
            print(f'warning: no choice name for question "{question_name}"')
        # add assignments
        assignments_dict = OrderedDict()
        if assignments is not None:
            for _, row in assignments.iterrows():
                if row['assign_if_question'] == question_name:
                    assignments_dict[
                        row['assign_if_value']
                    ] = row['assign_to_group']
            question['assignments'] = assignments_dict
        # add dependencies
        dependencies_list = []
        if dependencies is not None:
            for _, row in dependencies.iterrows():
                if row['dependent'] == question_name:
                    dependencies_list.append(Dependency(
                        dependency_type=row['dependency_type'],
                        independent=row['independent'],
                        choices=row['choice'].split('\n')
                        if notnull(row['choice']) else None,
                        condition=row['condition']
                        if notnull(row['condition']) else None
                    ))
            question['dependencies'] = dependencies_list
        # add terminations
        terminations_list = []
        if terminations is not None:
            for _, row in terminations.iterrows():
                if row['question'] == question_name:
                    terminations_list.append(Termination(
                        choices=row['choices'].split('\n')
                        if notnull(row['choices']) else None,
                        termination_type=row['termination_type'],
                        value=row['value'] if notnull(row['value']) else None,
                        otherwise=row['otherwise']
                        if notnull(row['otherwise']) else None
                    ))
            question['terminations'] = terminations_list

        # add ask_to
        if ask_to is not None:
            question['ask_to'] = ask_to

        return SurveyQuestion(**question)

    def to_html(self) -> str:
        """
        Write the question text and markup to an html string.
        """
        str_out = spaces(4) + f'<li><b>{self.text}</b>'
        # ask to
        if self.ask_to:
            str_out += bold_blue(
                f'[ASK TO {comma_and(self.ask_to, capitalize=True)}]'
            )
        # dependencies
        if self.dependencies:
            for dependency in self.dependencies:
                str_out += bold_blue(dependency.to_html(parent=self.parent))
        # randomize
        if self.randomize:
            str_out += bold_blue('[RANDOMIZE]')
        # terminations
        if self.terminations:
            for termination in self.terminations:
                str_out += bold_red(termination.to_html())
        # notes
        if self.notes:
            for note in self.notes:
                str_out += bold_blue(f'[{note}]')
        str_out += '</li>\n'
        if self.choices:
            str_out += spaces(4) + '<ol type="a">\n'
            for choice in self.choices:
                str_out += spaces(8) + f'<li>{choice}'
                if choice in self.assignments.keys():
                    str_out += bold_blue(
                        f'[Assign to group "{self.assignments[choice]}"]'
                    )
                str_out += '</li>\n'
            str_out += spaces(4) + '</ol>\n'
        return str_out

    def __str__(self):

        str_out = (
            f'[{self.name}]\n'
            f'{self.text}\n'
        )
        if self.choices:
            for choice in self.choices:
                str_out += f'\t• {choice}\n'
        return str_out
