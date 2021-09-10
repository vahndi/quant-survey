import unittest
from typing import Dict
from unittest.case import TestCase

from survey import Survey
from survey.surveys.survey_creators.alpha_hq_creator import AlphaHQCreator
from tests.test_survey_creators.utils import get_surveys_dir, get_metadata_path


def create_survey(survey_number: int) -> Survey:

    survey_path = get_surveys_dir('alpha_hq') / f'test_{survey_number}_data.csv'
    creator = AlphaHQCreator(
        survey_name='survey_{survey_number}',
        survey_data_fn=survey_path,
        metadata_fn=get_metadata_path('alpha_hq'),
        survey_id_col='survey_number',
        survey_id=survey_number
    )
    survey = creator.run()
    return survey


class TestAlphaHqCreator(TestCase):

    def setUp(self) -> None:

        self.checks = {
            47: {
                'num_questions': 7,
                'num_respondents': 211,
                'num_attributes': 4,
            },
            53: {
                'num_questions': 13,
                'num_respondents': 390,
                'num_attributes': 4,
            },
            69: {
                'num_questions': 5,
                'num_respondents': 402,
                'num_attributes': 4,
            }
        }
        self.surveys: Dict[int, Survey] = {}
        for survey_num in (47, 53, 69):
            self.surveys[survey_num] = create_survey(survey_num)

    def test_create_47(self):
        self.assertIsInstance(self.surveys[47], Survey)

    def test_create_53(self):
        self.assertIsInstance(self.surveys[53], Survey)

    def test_create_69(self):
        self.assertIsInstance(self.surveys[69], Survey)

    def test_num_questions(self):

        for survey_num in (47, 53, 69):
            self.assertEqual(self.checks[survey_num]['num_questions'],
                             len(self.surveys[survey_num].questions.to_list()))

    def test_num_respondents(self):

        for survey_num in (47, 53, 69):
            self.assertEqual(self.checks[survey_num]['num_respondents'],
                             self.surveys[survey_num].num_respondents)

    def test_num_attributes(self):

        for survey_num in (47, 53, 69):
            self.assertEqual(self.checks[survey_num]['num_attributes'],
                             len(self.surveys[survey_num].attributes.to_list()))


if __name__ == '__main__':

    unittest.main()
