from numpy import array, nan
from pandas import Series, DataFrame
from unittest.case import TestCase

from probability.distributions import Beta

from survey.questions import SingleChoiceQuestion


class TestSingleChoiceQuestion(TestCase):

    def setUp(self) -> None:

        self.question = SingleChoiceQuestion(
            name='single_choice_question',
            text='Single Choice Question',
            categories=['apples', 'bananas', 'cherries', 'dates'],
            ordered=False,
            data=Series([
                'apples', 'apples', 'apples',
                'bananas', 'bananas', 'cherries'
            ])
        )
        self.question_with_nulls = SingleChoiceQuestion(
            name='single_choice_question_with_nulls',
            text='Single Choice Question with Nulls',
            categories=['apples', 'bananas', 'cherries', 'dates'],
            ordered=False,
            data=Series([
                'apples', 'apples', 'apples',
                'bananas', 'bananas', 'cherries',
                nan, nan, nan
            ])
        )

    def test_count(self):

        self.assertEqual(6, self.question.count())
        self.assertEqual(6, self.question_with_nulls.count())
        self.assertEqual(3, self.question.count('apples'))
        self.assertEqual(3, self.question_with_nulls.count('apples'))
        self.assertEqual(5, self.question.count(['apples', 'bananas']))
        self.assertEqual(5, self.question_with_nulls.count([
            'apples', 'bananas'
        ]))

    def test_counts(self):

        all_counts = Series({
            'apples': 3,
            'bananas': 2,
            'cherries': 1,
            'dates': 0
        })
        apple_counts = Series({'apples': 3})
        apple_banana_counts = Series({'apples': 3, 'bananas': 2})
        self.assertTrue(all_counts.equals(self.question.counts()))
        self.assertTrue(all_counts.equals(self.question_with_nulls.counts()))
        self.assertTrue(apple_counts.equals(self.question.counts('apples')))
        self.assertTrue(apple_counts.equals(
            self.question_with_nulls.counts('apples'))
        )
        self.assertTrue(apple_banana_counts.equals(self.question.counts([
            'apples', 'bananas'
        ])))
        self.assertTrue(
            apple_banana_counts.equals(self.question_with_nulls.counts([
                'apples', 'bananas'
            ]))
        )

    def test_distribution_table__no_significance(self):

        expected = DataFrame(data=[
            ('apples', 3),
            ('bananas', 2),
            ('cherries', 1),
            ('dates', 0)
        ], columns=['Value', 'Count'])
        actual = self.question.distribution_table()
        self.assertTrue(expected.equals(actual))

    def test_distribution_table__significance(self):

        a = array([3, 2, 1, 0])
        n = a.sum()
        b = n - a
        a_others = array([
            (a.sum() - a[i]) / (len(a) - 1)
            for i in range(len(a))
        ])
        b_others = n - a_others

        expected = DataFrame(data=[
            ('apples', a[0],
             Beta(1 + a[0], 1 + b[0]) > Beta(1 + a_others[0], 1 + b_others[0])),
            ('bananas', a[1],
             Beta(1 + a[1], 1 + b[1]) > Beta(1 + a_others[1], 1 + b_others[1])),
            ('cherries', a[2],
             Beta(1 + a[2], 1 + b[2]) > Beta(1 + a_others[2], 1 + b_others[2])),
            ('dates', a[3],
             Beta(1 + a[3], 1 + b[3]) > Beta(1 + a_others[3], 1 + b_others[3])),
        ], columns=['Value', 'Count', 'Significance'])
        actual = self.question.distribution_table(significance=True)
        self.assertTrue(expected.equals(actual))
