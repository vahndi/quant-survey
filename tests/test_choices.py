from pandas import DataFrame
import random
from unittest import TestCase

from survey.surveys.survey_creators.choices import get_likert_choices


class TestChoices(TestCase):

    def setUp(self) -> None:

        self.numeric_string = [
            '1 Extremely negative',
            '2', '3', '4', '5', '6',
            '7 Extremely positive'
        ]
        self.numeric = [1, 2, 3, 4, 5, 6, 7]
        self.string = ['medium', 'low', 'high']

        self.string_order = ['low', 'medium', 'high']
        self.reverse_numeric_order = [7, 6, 5, 4, 3, 2, 1]
        self.reverse_numeric_string_order = [
            '7 Extremely positive',
            '6', '5', '4', '3', '2',
            '1 Extremely negative'
        ]

        self.ordered_test_combos = [
            (self.numeric_string, self.numeric_string),
            (self.numeric_string, self.reverse_numeric_string_order),
            (self.numeric, self.numeric),
            (self.numeric, self.reverse_numeric_order),
            (self.string, self.string_order)
        ]
        self.unordered_test_combos = [
            (self.numeric_string, self.numeric_string),
            (self.numeric, self.numeric)
        ]

    def test_get_likert_choices_with_order(self):

        for format_, expected_order in self.ordered_test_combos:
            orders_meta = DataFrame({
                'category': 'question_1',
                'value': c
            } for c in expected_order)
            survey_data = DataFrame({
                'question_1': random.choice(format_)
            } for _ in range(100))
            expected_choices = {
                str(expected_order[i]): i + 1
                for i in range(len(expected_order))
            }
            choices = get_likert_choices(orders_meta=orders_meta,
                                         survey_data=survey_data,
                                         question_name='question_1')
            self.assertEqual(expected_choices, choices)

    def test_get_numeric_likert_choices_no_order(self):

        for format_, expected_order in self.unordered_test_combos:
            orders_meta = DataFrame({
                'category': 'question_2',
                'value': c
            } for c in expected_order)
            survey_data = DataFrame({
                'question_1': random.choice(format_)
            } for _ in range(100))
            expected_choices = {
                str(expected_order[i]): i + 1
                for i in range(len(expected_order))
            }
            choices = get_likert_choices(orders_meta=orders_meta,
                                         survey_data=survey_data,
                                         question_name='question_1')
            self.assertEqual(choices, expected_choices)
