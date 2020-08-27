from pandas import read_csv


def print_column_headers(survey_fn: str):

    data = read_csv(survey_fn, header=1)
    for column in data.columns:
        print(column)


if __name__ == '__main__':

    print_column_headers('/Users/vahndi.minah/Desktop/gitcode/dev/frog_survey/assets/surveys/qualtrics/surveys/'
                         'Deliveroo_Kit_ENGLISH_AUSTRALIA_May+5,+2019_18.36.csv')
