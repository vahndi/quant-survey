from collections import OrderedDict
import unittest
from unittest.case import TestCase
from numpy import nan
from pandas import Series, ExcelFile, read_excel, Index

from survey.groups.question_groups.single_choice_question_group import \
    SingleChoiceQuestionGroup
from survey.questions import SingleChoiceQuestion
from tests.paths.files import FN_STACK_DATA


class TestSingleCategoryGroupPTMixin(TestCase):

    def setUp(self) -> None:

        xlsx = ExcelFile(FN_STACK_DATA)

        self.gender_data = read_excel(xlsx, 'gender')
        gender_questions = OrderedDict()
        for g, group in enumerate(self.gender_data.columns):
            question_data = Series(
                data=nan, name='gender',
                index=Index(data=range(1, 101), name='Respondent ID')
            )
            question_data.loc[
                g * 10 + 1: (g + 1) * 10
            ] = self.gender_data[group].to_list()
            question = SingleChoiceQuestion(name='gender', text='Gender',
                                            categories=['Female', 'Male'],
                                            ordered=False, data=question_data)
            gender_questions[group] = question
        self.gender_group = SingleChoiceQuestionGroup(
            questions=gender_questions
        )

        self.preference_data = read_excel(xlsx, 'preference')
        preference_questions = OrderedDict()
        for g, group in enumerate(self.preference_data.columns):
            question_data = Series(
                data=nan, name='preference',
                index=Index(data=range(1, 101), name='Respondent ID')
            )
            question_data.loc[
                g * 10 + 1: (g + 1) * 10
            ] = self.preference_data[group].to_list()
            question = SingleChoiceQuestion(
                name='preference', text='Preference',
                categories=['Product 1', 'Product 2'],
                ordered=False, data=question_data
            )
            preference_questions[group] = question
        self.preference_group = SingleChoiceQuestionGroup(
            questions=preference_questions
        )

    def test_gender_cpt(self):

        cpt = self.gender_group.cpt()
        for group, row in cpt.iterrows():
            for category in self.gender_group.category_names:
                expected = (
                    self.gender_data[group].to_list().count(category) /
                    len(self.gender_data[group])
                )
                self.assertEqual(expected, row[category])

    def test_preference_cpt(self):

        cpt = self.preference_group.cpt()
        for group, row in cpt.iterrows():
            for category in self.preference_group.category_names:
                expected = (
                    self.preference_data[group].to_list().count(category) /
                    len(self.preference_data[group])
                )
                self.assertEqual(expected, row[category])

    def test_gender_jpt(self):

        jpt = self.gender_group.jpt()
        for group, row in jpt.iterrows():
            for category in self.gender_group.category_names:
                expected = (
                    self.gender_data[group].to_list().count(category) /
                    (self.gender_data.shape[0] * self.gender_data.shape[1])
                )
                self.assertEqual(expected, row[category])

    def test_preference_jpt(self):

        jpt = self.preference_group.jpt()
        for group, row in jpt.iterrows():
            for category in self.preference_group.category_names:
                expected = (
                    self.preference_data[group].to_list().count(category) /
                    (self.preference_data.shape[0] * self.gender_data.shape[1])
                )
                self.assertEqual(expected, row[category])


if __name__ == '__main__':

    unittest.main()
