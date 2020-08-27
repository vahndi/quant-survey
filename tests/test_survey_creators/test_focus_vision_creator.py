import unittest
from unittest.case import TestCase

from survey import Survey
from survey.surveys.survey_creators.focus_vision_creator import FocusVisionCreator
from tests.test_survey_creators.utils import get_surveys_dir, get_metadata_path


class TestFocusVisionCreator(TestCase):

    def setUp(self) -> None:

        survey_path = get_surveys_dir('focus_vision') / 'Sample Raw Data (Text).xlsx'
        creator = FocusVisionCreator(
            survey_name='Sample FocusVision Survey',
            survey_data_fn=survey_path,
            metadata_fn=get_metadata_path('focus_vision'),
        )
        self.survey = creator.run()

    def test_create(self):

        self.assertIsInstance(self.survey, Survey)

    def test_num_attributes(self):

        self.assertEqual(5, len(self.survey.attributes.to_list()))

    def test_num_questions(self):

        self.assertEqual(4, len(self.survey.questions.to_list()))

    def test_num_respondents(self):

        self.assertEqual(300, self.survey.num_respondents)


if __name__ == '__main__':

    unittest.main()
