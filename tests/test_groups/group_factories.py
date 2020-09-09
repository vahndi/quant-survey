from random import choices, seed

from numpy import array
from pandas import Series

from survey.questions import LikertQuestion
from survey.groups import LikertQuestionGroup


def make_likert_question_group() -> LikertQuestionGroup:

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
        questions[f'q_{q}'] = LikertQuestion(
            name=name, text=f'Question {q}',
            categories=categories, data=data
        )

    group = LikertQuestionGroup(questions)

    return group
