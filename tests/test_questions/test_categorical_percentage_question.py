from unittest.case import TestCase

from numpy import nan
from pandas import DataFrame

from tests.test_questions.question_factories import \
    make_categorical_percentage_question


class TestCategoricalPercentageQuestion(TestCase):

    def setUp(self) -> None:

        self.question = make_categorical_percentage_question()

    def test_make_features(self):

        name = self.question.name
        expected = DataFrame([
            {f'{name}: Work': 10, f'{name}: Play': 20, f'{name}: Sleep': 70},
            {f'{name}: Work': 50, f'{name}: Play': 35, f'{name}: Sleep': 15},
            {f'{name}: Work': 60, f'{name}: Play': 40, f'{name}: Sleep': 0},
        ])[[f'{name}: Work', f'{name}: Play', f'{name}: Sleep']]
        actual = self.question.make_features()
        assert(expected.equals(actual))

    def test_make_features_no_drop(self):

        name = self.question.name
        expected = DataFrame([
            {f'{name}: Work': 10, f'{name}: Play': 20, f'{name}: Sleep': 70},
            {f'{name}: Work': 50, f'{name}: Play': 35, f'{name}: Sleep': 15},
            {f'{name}: Work': nan, f'{name}: Play': nan, f'{name}: Sleep': nan},
            {f'{name}: Work': 60, f'{name}: Play': 40, f'{name}: Sleep': 0}
        ])[[f'{name}: Work', f'{name}: Play', f'{name}: Sleep']]
        actual = self.question.make_features(drop_na=False)
        print(expected)
        print(actual)
        assert(expected.equals(actual))
