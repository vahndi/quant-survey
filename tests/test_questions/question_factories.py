from pandas import Series

from survey.questions import LikertQuestion


def make_likert_question() -> LikertQuestion:

    categories = {
        '1 - strongly disagree': 1,
        '2 - disagree': 2,
        '3 - neither agree nor disagree': 3,
        '4 - agree': 4,
        '5 - strongly agree': 5
    }
    data = Series(
        ['1 - strongly disagree'] * 2 +
        ['2 - disagree'] * 4 +
        ['3 - neither agree nor disagree'] * 6 +
        ['5 - strongly agree'] * 3
    )
    question = LikertQuestion(
        name='test_likert_question',
        text='Test Likert Question',
        categories=categories,
        data=data
    )
    return question
