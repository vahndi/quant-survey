from pandas import DataFrame
from pprint import pprint

from survey.surveys.provider_utils.usability_hub import get_question_text


def summarize(survey_data: DataFrame):
    """
    Summarize the questions and attributes of a survey.

    :param survey_data: The data of the survey to summarize.
    """
    # print names of questions and attributes
    print('Questions and Attributes')
    print('========================\n')
    for col in survey_data.columns:
        print(col)
    pprint(survey_data.columns.tolist())
    for column in survey_data.columns:
        print()
        print(column)
        question_text = get_question_text(column)
        if question_text != column:
            print(question_text)
        print('=' * len(column))
        if survey_data[column].dtype == object:
            values = sorted(set([
                value
                for _, row in survey_data[column].dropna().items()
                for value in row.split('; ')
            ]))
        else:
            values = survey_data[column].unique().tolist()
        if len(values) < 20:
            for value in values:
                print(value)


def print_questions_attributes(survey_data: DataFrame):

    for col in survey_data.columns:
        print(get_question_text(col))
