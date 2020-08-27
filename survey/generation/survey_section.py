from typing import Optional, List

from survey.generation.formatting import bold_blue
from survey.generation.mixins.name_index_mixin import NameIndexMixin
from survey.generation.survey_question import SurveyQuestion


class SurveySection(NameIndexMixin, object):
    """
    Class to represent a Survey Section.
    """
    def __init__(self, questions: Optional[List[SurveyQuestion]] = None,
                 name: Optional[str] = None,
                 notes: Optional[List[str]] = None,
                 intro: Optional[str] = None):
        """
        Create a new Survey Section.

        :param questions: Optional list of Questions to instantiate the Section.
        :param name: Optional name for the Survey Section.
        :param notes: Optional list of notes for the Survey Programmers.
        :param intro: Optional introductory text to show the Respondents.
        """
        if questions is not None:
            question_names = [q.name for q in questions]
            if len(question_names) != len(set(question_names)):
                non_unique = [q for q in question_names
                              if question_names.count(q) > 1]
                raise ValueError(f'Question names must be unique. '
                                 f'These are not: {non_unique}')
        self.questions: List[SurveyQuestion] = []
        if questions:
            self.questions = questions
        for question in self.questions:
            question.parent = self
        self.name: Optional[str] = name
        self.intro: Optional[str] = intro
        self.notes: List[str] = notes or []

    @property
    def question_names(self) -> List[str]:
        """
        Return the list of names of questions in the Section.
        """
        return [q.name for q in self.questions]

    def append(self, question: SurveyQuestion):
        """
        Add a new question to the Section.
        """
        self.questions.append(question)
        question.parent = self

    def to_html(self, start_at: int = 1) -> str:
        """
        Write the section to an html string.

        :param start_at: Number to start the first question at.
        """
        str_out = ''
        if self.name is not None:
            str_out += f'<h2>{self.name}</h2>\n'
        if self.notes:
            for note in self.notes:
                str_out += bold_blue(f'[{note}]\n')
        if self.intro is not None:
            str_out += f'<b><i>{self.intro}</i></b>\n'
        str_out += f'<ol type="1" start="{start_at}">\n'
        for question in self.questions:
            str_out += question.to_html()
        str_out += '</ol>\n'

        return str_out

    def __len__(self):
        """
        Return the length of the Section in Questions.
        """
        return len(self.questions)

    def __add__(self, other: 'SurveySection') -> 'SurveySection':
        """
        Combine with another Section. Loses name, notes and intro.
        """
        return SurveySection(
            questions=[q for q in self.questions] +
                      [q for q in other.questions]
        )
