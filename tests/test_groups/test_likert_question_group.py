from unittest.case import TestCase

from mpl_format.figures.figure_formatter import FigureFormatter
from numpy import array
from random import seed, choices

from pandas import Series

from survey.groups.question_groups.likert_question_group import \
    LikertQuestionGroup
from survey.questions import LikertQuestion


class TestLikertQuestionGroup(TestCase):

    def setUp(self) -> None:

        categories = {
            'Strongly Disagree': 1,
            'Disagree': 2,
            'Neither Agree Nor Disagree': 3,
            'Agree': 4,
            'Strongly Agree': 5
        }

        seed(0)
        questions = {}
        for q in range(12):
            weights = array([1 / (1 + abs(q - a) % 5) for a in range(5)])
            weights /= weights.sum()
            data = Series(choices(
                population=list(categories.keys()), weights=weights, k=100
            ))
            name = f'question_{q}'
            questions[name] = LikertQuestion(
                name=name, text=f'Question {q}',
                categories=categories, data=data
            )

        group = LikertQuestionGroup(questions)
        self.fig = group.plot_distribution_grid(
            n_rows=3, n_cols=4, significance=True,
            group_significance=True
        )
        self.green_color = (0.0, 1.0, 0.0, 1.0)
        self.red_color = (1.0, 0.0, 0.0, 1.0)

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
