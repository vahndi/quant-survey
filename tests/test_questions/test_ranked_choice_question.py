from collections import defaultdict
from unittest.case import TestCase
from numpy.random import permutation
from numpy.random.mtrand import RandomState
from pandas import Series

from survey.questions import RankedChoiceQuestion


class TestRankedChoiceQuestion(TestCase):

    def setUp(self) -> None:

        RandomState(0)
        self.choices = [f'Option {choice}' for choice in range(1, 11)]
        perms = [permutation(self.choices) for _ in range(100)]
        self.expected_ranks = defaultdict(int)
        for perm in perms:
            for rank, option in enumerate(perm):
                self.expected_ranks[(option, rank + 1)] += 1
        data = Series(['\n'.join(perm) for perm in perms])
        self.question = RankedChoiceQuestion(
            name='ranked_choice_question',
            text='Ranked Choice Question',
            categories=self.choices,
            data=data
        )

    def test_distribution_table__no_significance(self):

        table = self.question.distribution_table()
        for option in self.choices:
            for rank in range(1, 11):
                self.assertEqual(
                    self.expected_ranks[option, rank],
                    table.loc[option, rank]
                )

    def test_distribution__significance(self):

        table = self.question.distribution_table(significance=True)
        for option in self.choices:
            for rank in range(1, 11):
                self.assertEqual(
                    self.expected_ranks[option, rank],
                    table.loc[option, rank]
                )
        significance = self.question.significance__one_vs_any()
        self.assertTrue(significance.equals(table['Significance']))
