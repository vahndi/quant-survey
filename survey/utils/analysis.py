from pandas import DataFrame, Series
from itertools import product

from survey.attributes import SingleCategoryAttribute
from survey.questions import SingleChoiceQuestion
from survey.surveys.survey import Survey
from survey.utils.processing import match_all


def analyze_responses_by_attribute(
        survey: Survey,
        question: SingleChoiceQuestion,
        attribute: SingleCategoryAttribute,
        group_values: bool,
        join_str: str = ' || '
) -> DataFrame:
    """
    Analyze responses to a question between respondents with different values of
    an attribute.
    Leads to statements of the form "respondents with an attribute value of X
    are Y%  more likely to answer Z than respondents with an attribute value of
    ~X" e.g. "men are 50% more likely to switch plans than women".

    :param survey: Survey containing the question and respondents to analyze.
    :param question: The question to analyze.
    :param attribute: The attribute of the respondents to analyze.
    :param group_values: Whether to group experimental and control group
                         attribute values and answers into single columns.
    :param join_str: String to use to join grouped list items.
    :return: DataFrame with columns of answers and attribute values,
             set to True where tested, and the result.
    """
    results_list = []

    # iterate over groups of respondent attribute values and answer choices
    for (attrs_exp, attrs_ctl), (answers_given, answers_not_given) in product(
        attribute.group_pairs(), question.group_pairs()
    ):
        prob_result = survey.prob_superior(
            question=question, attribute=attribute,
            exp_attr_values=attrs_exp, exp_answers=answers_given,
            ctl_attr_values=attrs_ctl, ctl_answers=answers_given
        )
        # compile result data
        if group_values:
            result = dict(
                survey_name=survey.name,
                survey_question=question.name,
                attribute_name=attribute.name
            )
            result['attr_vals_experimental'] = join_str.join(attrs_exp)
            result['attr_vals_control'] = join_str.join(attrs_ctl)
            result['answers_given'] = join_str.join(answers_given)
            result['answers_not_given'] = join_str.join(answers_not_given)
            result['p_superior'] = prob_result.p_superior
            result['exp_mean - ctl_mean'] = (
                    prob_result.experimental_mean -
                    prob_result.control_mean
            )
            result['exp_mean'] = prob_result.experimental_mean
            result['ctl_mean'] = prob_result.control_mean
        else:
            result = {
                ('survey', 'name'): survey.name,
                ('survey', 'question'): question.name,
            }
            for attr in attrs_exp:
                result[(attribute.name, attr)] = True
            for attr in attrs_ctl:
                result[(attribute.name, attr)] = False
            for answer in answers_given:
                result[('answer', answer)] = True
            for answer in answers_not_given:
                result[('answer', answer)] = False
            result[('result', 'p_superior')] = prob_result.p_superior
            result[('result', 'exp_mean - ctl_mean')] = (
                prob_result.experimental_mean - prob_result.control_mean
            )
            result[('result', 'exp_mean')] = prob_result.experimental_mean
            result[('result', 'ctl_mean')] = prob_result.control_mean
        results_list.append(result)

    # compile respondent category results
    if group_values:
        results = DataFrame(results_list)[
            ['survey_name', 'survey_question', 'attribute_name'] +
            ['attr_vals_experimental', 'attr_vals_control'] +
            ['answers_given',  'answers_not_given'] +
            ['p_superior', 'exp_mean - ctl_mean', 'exp_mean', 'ctl_mean']
        ]
    else:
        results = DataFrame(results_list)[
            [('survey', 'name'), ('survey', 'question')] +
            [(attribute.name, attr_value)
             for attr_value in attribute.categories] +
            [('answer', answer) for answer in question.categories] +
            [('result', 'p_superior'), ('result', 'exp_mean - ctl_mean'),
             ('result', 'exp_mean'), ('result', 'ctl_mean')]
            ]

    return results


def prune_results(results: DataFrame,
                  question: SingleChoiceQuestion,
                  attribute: SingleCategoryAttribute) -> DataFrame:
    """
    Prune responses to question analyses.

    :param results: The results of the analysis.
    :param question: The question that was tested.
    :param attribute: The attribute that was tested.
    """
    results = results.sort_values('p_superior', ascending=False)
    answers = question.category_names
    ix_drop = Series(data=[False] * len(results), index=results.index)
    # prune for case 1
    for ix, row in results.iterrows():
        # find rows with the same respondent values
        used_values = row[attribute.categories].to_dict()
        ix_same_resp_vals = match_all(results, used_values, exclude_ix=ix)
        # find rows with superset of this row's answer values
        used_answers = row[answers].loc[row[answers] == True].to_dict()
        ix_contains_answers = match_all(results, used_answers, exclude_ix=ix)
        ix_drop = ix_drop | (ix_same_resp_vals & ix_contains_answers)

    return results.loc[~ix_drop]
