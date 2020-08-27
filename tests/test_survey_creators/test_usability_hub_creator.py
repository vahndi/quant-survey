import unittest
from unittest.case import TestCase

from survey import Survey
from survey.surveys.survey_creators.usability_hub_creator import UsabilityHubCreator
from tests.test_survey_creators.utils import get_surveys_dir, get_metadata_path


class TestUsabilityHubCreator(TestCase):

    def setUp(self) -> None:

        survey_path = (
            get_surveys_dir('usability_hub') /
            f'WMAP Demo Survey-results_cleaned.csv'
        )
        creator = UsabilityHubCreator(
            survey_name='survey_{survey_number}',
            survey_data_fn=survey_path,
            metadata_fn=get_metadata_path('usability_hub'),
            survey_id_col='survey_number',
        )
        self.survey = creator.run()

    def test_create(self):

        self.assertIsInstance(self.survey, Survey)

    def test_num_attributes(self):

        self.assertEqual(2, len(self.survey.attributes.to_list()))

    def test_num_questions(self):

        self.assertEqual(25, len(self.survey.questions.to_list()))

    def test_num_respondents(self):

        self.assertEqual(112, self.survey.num_respondents)


if __name__ == '__main__':

    unittest.main()
