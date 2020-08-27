from unittest.case import TestCase

from pandas import Series, DataFrame

from survey.questions import FreeTextQuestion
from tests.test_data.testing_text import (
    CICERO_EN, LI_EUROPAN_LINGUES_EN, FAR_FAR_AWAY, WERTHER, KAFKA, PANGRAM
)


class TestFreeTextQuestion(TestCase):

    def setUp(self) -> None:
        data = Series([
            CICERO_EN, LI_EUROPAN_LINGUES_EN,
            FAR_FAR_AWAY, WERTHER, KAFKA, PANGRAM
        ])
        self.question = FreeTextQuestion(
            name='sample_texts', text='Sample Texts', data=data
        )

    def test_distribution_table(self):

        expected = DataFrame(data=[
            ('language', 12),
            ('pleasure', 8),
            ('quick', 8),
            ('quiz', 7),
            ('common', 6),
            ('fox', 6),
            ('one', 6),
            ('grammar', 5),
            ('pain', 5),
            ('vex', 5),
            ('bad', 4),
            ('blind', 4),
            ('existence', 4),
            ('far', 4),
            ('jump', 4),
            ('like', 4),
            ('little', 4),
            ('text', 4),
            ('word', 4),
        ], columns=['Word', 'Count'])
        actual = self.question.distribution_table(top=19)
        self.assertTrue(expected.equals(actual))
