import re

from pandas import DataFrame

re_question = re.compile(r'\(.+\) \(.+: "(.+)"\) Answer')


def get_question_text(text: str) -> str:

    match = re_question.search(text)
    if not match:
        return text
    else:
        return match.groups()[0]


def clean_question_names(survey_data: DataFrame) -> DataFrame:

    survey_data = survey_data.rename(columns={
        column: get_question_text(column)
        for column in survey_data.columns
    })
    return survey_data
