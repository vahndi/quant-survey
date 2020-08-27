from numpy import array
from pandas import Series, DataFrame
from unittest.case import TestCase
from probability.distributions import Beta

from survey.questions import LikertQuestion


class TestLikertQuestion(TestCase):

    def setUp(self) -> None:

        categories = {
            '1 - strongly disagree': 1,
            '2 - disagree': 2,
            '3 - neither agree nor disagree': 3,
            '4 - agree': 4,
            '5 - strongly agree': 5
        }
        data = Series(
            ['1 - strongly disagree'] * 2 +
            ['2 - disagree'] * 4 +
            ['3 - neither agree nor disagree'] * 6 +
            ['5 - strongly agree'] * 3
        )
        self.question = LikertQuestion(
            name='test_likert_question',
            text='Test Likert Question',
            categories=categories,
            data=data
        )

    def test_distribution_table__no_significance(self):

        expected = DataFrame(data=[
            ('1 - strongly disagree', 2),
            ('2 - disagree', 4),
            ('3 - neither agree nor disagree', 6),
            ('4 - agree', 0),
            ('5 - strongly agree', 3)
        ], columns=['Value', 'Count'])
        actual = self.question.distribution_table()
        self.assertTrue(expected.equals(actual))

    def test_distribution_table__significance(self):

        a = array([2, 4, 6, 0, 3])
        n = a.sum()
        b = n - a
        a_others = array([
            (a.sum() - a[i]) / (len(a) - 1)
            for i in range(len(a))
        ])
        b_others = n - a_others

        expected = DataFrame(data=[
            ('1 - strongly disagree', a[0],
             Beta(1 + a[0], 1 + b[0]) > Beta(1 + a_others[0], 1 + b_others[0])),
            ('2 - disagree', a[1],
             Beta(1 + a[1], 1 + b[1]) > Beta(1 + a_others[1], 1 + b_others[1])),
            ('3 - neither agree nor disagree', a[2],
             Beta(1 + a[2], 1 + b[2]) > Beta(1 + a_others[2], 1 + b_others[2])),
            ('4 - agree', a[3],
             Beta(1 + a[3], 1 + b[3]) > Beta(1 + a_others[3], 1 + b_others[3])),
            ('5 - strongly agree', a[4],
             Beta(1 + a[4], 1 + b[4]) > Beta(1 + a_others[4], 1 + b_others[4]))
        ], columns=['Value', 'Count', 'Significance'])
        actual = self.question.distribution_table(significance=True)
        self.assertTrue(expected.equals(actual))
