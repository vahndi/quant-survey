from pandas import read_excel

from survey.surveys.survey_creators import SurveyCreator


class SurveyMonkeyCreator(SurveyCreator):

    def read_survey_data(self):

        data = read_excel(self.survey_data_fn)
        if self.pre_clean is not None:
            data = self.pre_clean(data)
        self.survey_data = data

