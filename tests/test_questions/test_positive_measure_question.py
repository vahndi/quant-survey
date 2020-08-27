from unittest.case import TestCase

from numpy.random.mtrand import RandomState
from pandas import DataFrame, Series
from probability.distributions import Exponential

from survey.questions import PositiveMeasureQuestion


class TestPositiveMeasureQuestion(TestCase):

    def setUp(self) -> None:

        RandomState(0)
        data = Series(Exponential(lambda_=0.5).rvs(100, random_state=0))
        self.question = PositiveMeasureQuestion(
            name='positive_measure_question',
            text='Positive Measure Question',
            data=data
        )

    def test_distribution_table__count_only(self):

        expected = DataFrame([
            (-0.5, 0.5, 27),
            (0.5, 1.5, 26),
            (1.5, 2.5, 24),
            (2.5, 3.5, 9),
            (3.5, 4.5, 5),
            (4.5, 5.5, 2),
            (5.5, 6.5, 2),
            (6.5, 7.5, 2),
            (7.5, 8.5, 2),
            (8.5, 9.5, 1),
        ], columns=['From Value', 'To Value', 'Count'])
        actual = self.question.distribution_table()
        self.assertTrue(expected.equals(actual))

    def test_distribution_table__percent_only(self):

        expected = DataFrame([
            (-0.5, 0.5, .27),
            (0.5, 1.5, .26),
            (1.5, 2.5, .24),
            (2.5, 3.5, .09),
            (3.5, 4.5, .05),
            (4.5, 5.5, .02),
            (5.5, 6.5, .02),
            (6.5, 7.5, .02),
            (7.5, 8.5, .02),
            (8.5, 9.5, .01),
        ], columns=['From Value', 'To Value', 'Percentage'])
        actual = self.question.distribution_table(count=False, percent=True)
        self.assertTrue(expected.equals(actual))

    def test_distribution_table__count_percent(self):

        expected = DataFrame([
            (-0.5, 0.5, 27, .27),
            (0.5, 1.5, 26, .26),
            (1.5, 2.5, 24, .24),
            (2.5, 3.5, 9, .09),
            (3.5, 4.5, 5, .05),
            (4.5, 5.5, 2, .02),
            (5.5, 6.5, 2, .02),
            (6.5, 7.5, 2, .02),
            (7.5, 8.5, 2, .02),
            (8.5, 9.5, 1, .01),
        ], columns=['From Value', 'To Value', 'Count', 'Percentage'])
        actual = self.question.distribution_table(count=True, percent=True)
        self.assertTrue(expected.equals(actual))
