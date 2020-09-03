from unittest.case import TestCase

from mpl_format.figures.figure_formatter import FigureFormatter
from pandas import Series, DataFrame

from survey.questions import LikertQuestion, CountQuestion
from tests.test_groups.group_factories import make_likert_question_group


class TestLikertQuestionGroup(TestCase):

    def setUp(self) -> None:

        self.group = make_likert_question_group()
        self.fig = self.group.plot_distribution_grid(
            n_rows=3, n_cols=4, significance=True,
            group_significance=True
        )
        self.green_color = (0.0, 1.0, 0.0, 1.0)
        self.red_color = (1.0, 0.0, 0.0, 1.0)

    def test_get_item__exists(self):

        self.assertIsInstance(self.group['q_1'], LikertQuestion)

    def test_get_item__does_not_exist(self):

        self.assertRaises(KeyError, self.group.__getitem__, 'q_12')

    def test_set_item__correct_type(self):

        new_question = self.group['q_0'].rename('question_x')
        self.group['q_x'] = new_question
        self.assertIsInstance(self.group['q_x'], LikertQuestion)

    def test_set_item__incorrect_type(self):

        new_question = CountQuestion(name='count_question',
                                     text='I am a CountQuestion',
                                     data=Series(data=[1, 2, 3, 4, 5]))
        self.assertRaises(TypeError, self.group.__setitem__, new_question)

    def test_value_counts(self):

        value_counts = DataFrame([
            ('q_0', 'Question 0', 'question_0', 28, 30, 12, 19, 11),
            ('q_1', 'Question 1', 'question_1', 22, 42, 19, 8, 9),
            ('q_2', 'Question 2', 'question_2', 14, 17, 38, 19, 12),
            ('q_3', 'Question 3', 'question_3', 12, 14, 13, 37, 24),
            ('q_4', 'Question 4', 'question_4', 13, 11, 6, 21, 49),
            ('q_5', 'Question 5', 'question_5', 51, 8, 7, 15, 19),
            ('q_6', 'Question 6', 'question_6', 22, 51, 9, 8, 10),
            ('q_7', 'Question 7', 'question_7', 17, 24, 43, 6, 10),
            ('q_8', 'Question 8', 'question_8', 11, 13, 22, 49, 5),
            ('q_9', 'Question 9', 'question_9', 11, 9, 15, 17, 48),
            ('q_10', 'Question 10', 'question_10',  36, 8, 15, 15, 26),
            ('q_11', 'Question 11', 'question_11',  25, 43, 6, 15, 11),
        ], columns=[
            'key', 'text', 'name',
            'Strongly Disagree', 'Disagree',
            'Neither Agree Nor Disagree',
            'Agree', 'Strongly Agree'
        ]).set_index(['key', 'text', 'name'])
        self.assertTrue(value_counts.equals(self.group.value_counts()))

    def test_plot_comparison_grid_question_significance(self):

        ff = FigureFormatter(self.fig)
        greens = [
            (0, 1), (1,), (2,), (3,), (4,), (0,),
            (1,), (2,), (3,), (4,), (0,), (1,)
        ]
        reds = [
            (2, 4), (3, 4), (4,), (0, 2), (0, 1, 2), (1, 2),
            (2, 3, 4), (3, 4), (0, 1, 4), (0, 1), (1,), (2, 4)
        ]
        for axf, green, red in zip(ff.multi.flat, greens, reds):
            edge_colors = axf.rectangles.edge_colors
            for g in green:
                self.assertEqual(edge_colors[g], self.green_color)
            for r in red:
                self.assertEqual(edge_colors[r], self.red_color)

    def test_plot_comparison_grid_question_significance(self):

        ff = FigureFormatter(self.fig)
        greens = [3, 4, 8, 9]
        reds = [0, 1, 5, 6, 11]
        for a, axf in zip(range(12), ff.multi.flat):
            frame_colors = axf.get_frame_colors()
            if a in greens:
                for fc in frame_colors:
                    self.assertEqual(fc, self.green_color)
            elif a in reds:
                for fc in frame_colors:
                    self.assertEqual(fc, self.red_color)
