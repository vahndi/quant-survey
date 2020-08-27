from numpy import array, nan
from pandas import Series, DataFrame
from probability.distributions import Beta
from unittest.case import TestCase

from survey.questions import MultiChoiceQuestion


class TestMultiChoiceQuestion(TestCase):

    def setUp(self) -> None:

        self.question = MultiChoiceQuestion(
            name='test_question',
            text='Test Question',
            categories=['apples', 'bananas', 'cherries'],
            ordered=False,
            data=Series([
                'apples',
                'apples\nbananas',
                'apples\nbananas\ncherries',
                nan
            ])
        )

    def test_count(self):

        self.assertEqual(3, self.question.count())
        self.assertEqual(3, self.question.count('apples'))
        self.assertEqual(2, self.question.count('bananas'))
        self.assertEqual(3, self.question.count(['apples', 'bananas'], 'any'))
        self.assertEqual(2, self.question.count(['apples', 'bananas'], 'all'))
        self.assertEqual(1, self.question.count([
            'apples', 'bananas', 'cherries'
        ], 'all'))

    def test_counts(self):

        counts = Series({'apples': 3, 'bananas': 2, 'cherries': 1})
        counts_apples_any = Series({'apples': 3, 'bananas': 2, 'cherries': 1})
        counts_bananas_any = Series({'apples': 2, 'bananas': 2, 'cherries': 1})
        counts_apples_all = Series({'apples': 3, 'bananas': 2, 'cherries': 1})
        counts_bananas_all = Series({'apples': 2, 'bananas': 2, 'cherries': 1})
        count_bc_any = Series({'apples': 2, 'bananas': 2, 'cherries': 1})
        count_bc_all = Series({'apples': 1, 'bananas': 1, 'cherries': 1})

        self.assertTrue(counts.equals(self.question.counts()))
        self.assertTrue(counts_apples_any.equals(
            self.question.counts('apples', 'any')
        ))
        self.assertTrue(counts_bananas_any.equals(
            self.question.counts('bananas', 'any')
        ))
        self.assertTrue(counts_apples_all.equals(
            self.question.counts('apples', 'all')
        ))
        self.assertTrue(counts_bananas_all.equals(
            self.question.counts('bananas', 'all')
        ))
        self.assertTrue(count_bc_any.equals(
            self.question.counts(['bananas', 'cherries'], 'any')
        ))
        self.assertTrue(count_bc_all.equals(
            self.question.counts(['bananas', 'cherries'], 'all')
        ))

    def test_num_selections(self):

        expected = Series([1, 2, 3])
        actual = self.question.num_selections()
        self.assertTrue(expected.equals(actual))

    def test_distribution_table__no_significance(self):

        expected = DataFrame(data=[
            ('apples', 3),
            ('bananas', 2),
            ('cherries', 1),
        ], columns=['Value', 'Count'])
        actual = self.question.distribution_table()
        self.assertTrue(expected.equals(actual))

    def test_distribution_table__significance(self):

        n_one = 3
        n_rest = 6
        a_one = array([3, 2, 1])
        b_one = n_one - a_one
        a_rest = array([sum(a_one) - a_one[i]
                        for i in range(len(a_one))])
        b_rest = n_rest - a_rest
        expected = DataFrame(data=[
            ('apples', 3,
             Beta(1 + a_one[0], 1 + b_one[0]) >
             Beta(1 + a_rest[0], 1 + b_rest[0])),
            ('bananas', 2,
             Beta(1 + a_one[1], 1 + b_one[1]) >
             Beta(1 + a_rest[1], 1 + b_rest[1])),
            ('cherries', 1,
             Beta(1 + a_one[2], 1 + b_one[2]) >
             Beta(1 + a_rest[2], 1 + b_rest[2])),
        ], columns=['Value', 'Count', 'Significance'])
        actual = self.question.distribution_table(significance=True)
        self.assertTrue(expected.equals(actual))
