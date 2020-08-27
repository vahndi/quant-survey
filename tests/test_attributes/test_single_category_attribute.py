from numpy import array
from pandas import Series, DataFrame
from unittest.case import TestCase

from probability.distributions import Beta

from survey.attributes import SingleCategoryAttribute


class TestSingleChoiceQuestion(TestCase):

    def setUp(self) -> None:

        self.attribute = SingleCategoryAttribute(
            name='single_category_attribute',
            text='Single Category Attribute',
            categories=['actor', 'bartender', 'cook', 'designer'],
            ordered=False,
            data=Series([
                'actor', 'actor', 'actor',
                'bartender', 'bartender', 'cook'
            ])
        )

    def test_distribution_table__no_significance(self):

        expected = DataFrame(data=[
            ('actor', 3),
            ('bartender', 2),
            ('cook', 1),
            ('designer', 0)
        ], columns=['Value', 'Count'])
        actual = self.attribute.distribution_table()
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
            ('actor', a[0],
             Beta(1 + a[0], 1 + b[0]) > Beta(1 + a_others[0], 1 + b_others[0])),
            ('bartender', a[1],
             Beta(1 + a[1], 1 + b[1]) > Beta(1 + a_others[1], 1 + b_others[1])),
            ('cook', a[2],
             Beta(1 + a[2], 1 + b[2]) > Beta(1 + a_others[2], 1 + b_others[2])),
            ('designer', a[3],
             Beta(1 + a[3], 1 + b[3]) > Beta(1 + a_others[3], 1 + b_others[3])),
        ], columns=['Value', 'Count', 'Significance'])
        actual = self.attribute.distribution_table(significance=True)
        self.assertTrue(expected.equals(actual))
