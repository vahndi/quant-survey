from pandas import DataFrame
import re
from typing import Union, List, Dict

from survey.constants import CATEGORY_SPLITTER


def get_choices(orders_meta: DataFrame,
                survey_data: DataFrame,
                question_name: str) -> Union[List[str], List[int]]:
    # check if user has specified order
    choices = orders_meta.loc[
        orders_meta['category'] == question_name, 'value'
    ].tolist()
    # if not specified, just return unique values as choices
    if len(choices) == 0:
        choices = survey_data[question_name].dropna().unique().tolist()
    return choices


def get_multi_choices(orders_meta: DataFrame,
                      survey_data: DataFrame,
                      question_name: str) -> List[str]:

    choices = orders_meta.loc[
        orders_meta['category'] == question_name, 'value'
    ].tolist()
    if len(choices) == 0:
        print(f'Warning - could not find categories for {question_name}.')
        uniques = survey_data[question_name].dropna().unique().tolist()
        choices = sorted(set([
            choice for str_choices in uniques for
            choice in str_choices.split(CATEGORY_SPLITTER)
        ]))
    return choices


def get_likert_choices(orders_meta: DataFrame,
                       survey_data: DataFrame,
                       question_name: str) -> Dict[str, int]:

    # determine if has numeric format e.g.  "1 abc", "2", 3 etc.
    orders_specified = len(orders_meta.loc[
        orders_meta['category'] == question_name, 'value'
    ]) > 0
    re_numeric = re.compile(r'(?:\d [\w ]+)|(?:\d)')
    choices = get_choices(orders_meta, survey_data, question_name)
    if not orders_specified:
        if all([isinstance(c, int) for c in choices]):
            choices = {str(c): c for c in choices}
        elif all([re_numeric.match(c) is not None for c in choices]):
            choices = {
                str(choice): int(choice.split()[0])
                for choice in choices
            }
        else:
            choices = {
                str(k): v + 1 for v, k in enumerate(choices)
            }
    else:
        choices = {
            str(k): v + 1 for v, k in enumerate(choices)
        }
    return choices
