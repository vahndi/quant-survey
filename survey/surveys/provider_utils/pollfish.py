# Collection of utils to find categories in raw data files
from pandas import DataFrame


def print_single_cat(data: DataFrame, question_name: str):

    for val in sorted(data[question_name].dropna().unique()):
        print(val)


def print_multi_cat(data: DataFrame, question_name: str):

    val_set = set()
    for str_vals in sorted(data[question_name].dropna().unique()):
        for val in str_vals.split(','):
            val_set.add(val)
    for val in sorted(val_set):
        print(val)


def print_multi_likert(data: DataFrame, question_name: str):

    question_data = data[question_name]
    print(question_data)
    for value in question_data.iloc[0].split(' | '):
        print(value)
    print(type(question_data))


def print_multi_choice(data: DataFrame, question_name: str):

    question_data = data[question_name]
    print(question_data)
    for value in question_data.iloc[0].split(' | '):
        print(value)
    print(type(question_data))
