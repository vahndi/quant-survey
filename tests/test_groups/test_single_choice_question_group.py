from numpy import nan
from unittest.case import TestCase

from pandas import Series

from survey.groups import SingleChoiceQuestionGroup
from survey.questions import SingleChoiceQuestion


class TestSingleChoiceQuestionGroup(TestCase):

    def setUp(self) -> None:

        self.group = SingleChoiceQuestionGroup(questions={
            f'question_{q}': SingleChoiceQuestion(
                name=f'question_{q}',
                text=f'Question {q}',
                categories=['apples', 'bananas', 'cherries'],
                data=Series(['apples'] * (q + 1) +
                            ['bananas'] * (q + 2) +
                            ['cherries'] * (q + 3) +
                            [nan]),
                ordered=True
            ) for q in range(3)
        })

    def test_count(self):

        self.assertEqual(6 + 9 + 12, self.group.count())
