import unittest
from unittest.case import TestCase

from survey import Survey
from survey.surveys.survey_creators.qualtrics_creator import QualtricsCreator
from tests.test_survey_creators.utils import get_surveys_dir, get_metadata_path


class TestQualtricsCreator(TestCase):

    def setUp(self) -> None:

        survey_path = (
            get_surveys_dir('qualtrics') /
            'Deliveroo_Kit_ENGLISH_AUSTRALIA_May+5,+2019_18.36.csv'
        )
        creator = QualtricsCreator(
            survey_name='Sample Qualtrics Survey',
            survey_data_fn=survey_path,
            metadata_fn=get_metadata_path('qualtrics'),
        )
        self.survey = creator.run()

    def test_create(self):

        self.assertIsInstance(self.survey, Survey)

    def test_num_attributes(self):

        self.assertEqual(4, len(self.survey.attributes.to_list()))

    def test_num_questions(self):

        self.assertEqual(53, len(self.survey.questions.to_list()))

    def test_num_respondents(self):

        self.assertEqual(544, self.survey.num_respondents)


if __name__ == '__main__':

    unittest.main()
