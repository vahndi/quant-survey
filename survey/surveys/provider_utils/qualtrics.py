from pandas import read_csv


def print_column_headers(survey_fn: str):

    data = read_csv(survey_fn, header=1)
    for column in data.columns:
        print(column)
