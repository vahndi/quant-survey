from pandas import Series, DataFrame
from unittest.case import TestCase

from survey.questions import CountQuestion


class TestCountQuestion(TestCase):

    def setUp(self) -> None:

        data = Series([3, 1, 4, 1, 5])
        self.question = CountQuestion(
            data=data, name='test_count_question',
            text='Test Count Question'
        )

    def test_distribution_table__count_only(self):

        expected = DataFrame([
            (-0.5, 0.5, 0),
            (0.5, 1.5, 2),
            (1.5, 2.5, 0),
            (2.5, 3.5, 1),
            (3.5, 4.5, 1),
            (4.5, 5.5, 1)
        ], columns=['From Value', 'To Value', 'Count'])
        self.assertTrue(expected.equals(self.question.distribution_table()))

    def test_distribution_table__percent_only(self):

        expected = DataFrame([
            (-0.5, 0.5, 0),
            (0.5, 1.5, 0.4),
            (1.5, 2.5, 0),
            (2.5, 3.5, .2),
            (3.5, 4.5, .2),
            (4.5, 5.5, .2)
        ], columns=['From Value', 'To Value', 'Percentage'])
        actual = self.question.distribution_table(count=False, percent=True)
        self.assertTrue(expected.equals(actual))

    def test_distribution_table__count_percent(self):

        expected = DataFrame([
            (-0.5, 0.5, 0, 0),
            (0.5, 1.5, 2, 0.4),
            (1.5, 2.5, 0, 0),
            (2.5, 3.5, 1, 0.2),
            (3.5, 4.5, 1, 0.2),
            (4.5, 5.5, 1, 0.2)
        ], columns=['From Value', 'To Value', 'Count', 'Percentage'])
        actual = self.question.distribution_table(count=True, percent=True)
        self.assertTrue(expected.equals(actual))
