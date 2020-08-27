import re

from survey.surveys.survey_creators.base.survey_creator import SurveyCreator


class UsabilityHubCreator(SurveyCreator):

    re_question = re.compile(r'\(.+\) \(.+: "(.+)"\) Answer')

    def _get_question_text(self, text: str) -> str:

        match = self.re_question.search(text)
        if not match:
            return text
        else:
            return match.groups()[0]

    def clean_survey_data(self):

        self.survey_data = self.survey_data.rename(
            columns={
                column: self._get_question_text(column)
                for column in self.survey_data.columns
            }
        )
