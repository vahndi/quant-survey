from unittest import TestCase

from survey import Survey
from survey.surveys.survey_creators.pollfish_creator import PollfishCreator
from tests.test_survey_creators.utils import get_surveys_dir, get_metadata_path


def create_survey() -> Survey:

    survey_path = get_surveys_dir('pollfish') / \
                  f'Pollfish_Example_Survey_253227526_en.xls'
    creator = PollfishCreator(
        survey_name='Pollfish Example Survey',
        survey_data_fn=survey_path,
        metadata_fn=get_metadata_path('pollfish')
    )
    survey = creator.run()
    return survey


class TestPollfishCreator(TestCase):

    def test_create_survey(self):
        survey = create_survey()
        self.assertIsInstance(survey, Survey)
