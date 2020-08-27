from typing import Optional, List

from survey.generation.survey_section import SurveySection


class SurveyDocument(object):
    """
    Class to generate a document that lays out the questions and logic of a
    survey. Composed of one or more sections e.g. "Screeners", "Demographics"
    """
    def __init__(self, sections: Optional[List[SurveySection]] = None,
                 name: Optional[str] = None):
        """
        Create a new SurveyDocument instance.

        :param sections: Optional list of sections to instantiate the
                         SurveyDocument.
        :param name: Optional name for the Survey.
        """
        self.sections = sections or []
        if sections is not None:
            for section in sections:
                section.name_index = self.name_index
        self.name: Optional[str] = name
        assert len(self.question_names) == len(set(self.question_names))

    @property
    def question_names(self) -> List[str]:
        """
        Return a list of the names of the survey questions in each section of
        the survey.
        """
        names = []
        for section in self.sections:
            names.extend(section.question_names)
        return names

    def append(self, section: SurveySection):
        """
        Append a new SurveySection to the SurveyDocument.

        :param section: Section to append.
        """
        assert not set(section.question_names).intersection(self.question_names)
        section.name_index = self.name_index
        self.sections.append(section)

    def name_index(self, question_name: str) -> Optional[int]:
        """
        Return the index of the question im the survey.

        :param question_name: Name of the question whose index to find.
        """
        names = self.question_names
        if question_name not in names:
            print(f'warning: question named {question_name} not found!')
            return None
        return names.index(question_name)

    def to_html(self) -> str:
        """
        Write the SurveyDocument to an html string.
        """
        str_out = ''
        if self.name is not None:
            str_out += f'<h1>{self.name}</h1>\n'
        start_question = 1
        for section in self.sections:
            str_out += section.to_html(start_question)
            start_question += len(section)
        return str_out
