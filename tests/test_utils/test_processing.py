from unittest import TestCase

from survey.utils.processing import get_group_pairs


class TestProcessing(TestCase):
    
    def setUp(self) -> None:
        
        self.groups = ['a', 'b', 'c', 'd']
        self.unordered_group_pairs_no_empty = [
            (['a', 'b', 'c'], ['d']),
            (['a', 'b', 'd'], ['c']),
            (['a', 'b'], ['c', 'd']),
            (['a', 'c', 'd'], ['b']),
            (['a', 'c'], ['b', 'd']),
            (['a', 'd'], ['b', 'c']),
            (['a'], ['b', 'c', 'd']),
            (['b', 'c', 'd'], ['a']),
            (['b', 'c'], ['a', 'd']),
            (['b', 'd'], ['a', 'c']),
            (['b'], ['a', 'c', 'd']),
            (['c', 'd'], ['a', 'b']),
            (['c'], ['a', 'b', 'd']),
            (['d'], ['a', 'b', 'c'])
        ]
        self.unordered_group_pairs_empty = [
            (['a', 'b', 'c', 'd'], []),
            (['a', 'b', 'c'], ['d']),
            (['a', 'b', 'd'], ['c']),
            (['a', 'b'], ['c', 'd']),
            (['a', 'c', 'd'], ['b']),
            (['a', 'c'], ['b', 'd']),
            (['a', 'd'], ['b', 'c']),
            (['a'], ['b', 'c', 'd']),
            (['b', 'c', 'd'], ['a']),
            (['b', 'c'], ['a', 'd']),
            (['b', 'd'], ['a', 'c']),
            (['b'], ['a', 'c', 'd']),
            (['c', 'd'], ['a', 'b']),
            (['c'], ['a', 'b', 'd']),
            (['d'], ['a', 'b', 'c']),
            ([], ['a', 'b', 'c', 'd'])
        ]
        self.ordered_group_pairs_no_empty = [
            (['a', 'b', 'c'], ['d']),
            (['a', 'b'], ['c', 'd']),
            (['a'], ['b', 'c', 'd']),
            (['b', 'c', 'd'], ['a']),
            (['c', 'd'], ['a', 'b']),
            (['d'], ['a', 'b', 'c'])
        ]
        self.ordered_group_pairs_empty = [
            (['a', 'b', 'c', 'd'], []),
            (['a', 'b', 'c'], ['d']),
            (['a', 'b'], ['c', 'd']),
            (['a'], ['b', 'c', 'd']),
            (['b', 'c', 'd'], ['a']),
            (['c', 'd'], ['a', 'b']),
            (['d'], ['a', 'b', 'c']),
            ([], ['a', 'b', 'c', 'd'])
        ]

    def test_get_unordered_group_pairs_no_empty(self):

        self.assertEqual(self.unordered_group_pairs_no_empty,
                         get_group_pairs(self.groups, ordered=False, include_empty=False))

    def test_get_ordered_group_pairs_no_empty(self):

        self.assertEqual(self.ordered_group_pairs_no_empty,
                         get_group_pairs(self.groups, ordered=True, include_empty=False))

    def test_get_unordered_group_pairs_empty(self):

        self.assertEqual(self.unordered_group_pairs_empty,
                         get_group_pairs(self.groups, ordered=False, include_empty=True))

    def test_get_ordered_group_pairs_empty(self):

        self.assertEqual(self.ordered_group_pairs_empty,
                         get_group_pairs(self.groups, ordered=True, include_empty=True))
