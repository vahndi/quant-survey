from typing import List, Union

from pandas import DataFrame, Series

from survey.utils.data_frames import count_coincidences


def create_cpt(prob_data: Union[DataFrame, Series],
               cond_data: Union[DataFrame, Series],
               prob_name: str, cond_name: str,
               prob_order: List[str], cond_order: List[str]) -> DataFrame:
    """
    Return a conditional probability table.

    :param prob_data: The Series or DataFrame containing the data to find the
                      probability of.
    :param cond_data: The Series or DataFrame containing the data to condition
                      on.
    :param prob_name: The name of the question or attribute to find probability
                      of.
    :param cond_name: The name of the question or attribute to condition on.
    :param prob_order: List of labels to order the probability values.
    :param cond_order: List of labels to order the conditioning values.
    :return: DataFrame of conditional probabilities with Index of `condition`
             and columns of `probability`.
    """
    if prob_name == cond_name:
        raise ValueError('prob_name must be different to cond_name')
    cp_table = count_coincidences(
        data_1=prob_data, data_2=cond_data,
        column_1=prob_name, column_1_order=prob_order,
        column_2=cond_name, column_2_order=cond_order
    )
    cp_table = cp_table.div(cp_table.sum(axis=1), axis=0)
    # order probabilities
    cp_table = cp_table[[p for p in prob_order if p in cp_table.columns]]
    # order conditions
    cp_table = cp_table.loc[[c for c in cond_order if c in cp_table.index]]

    return cp_table


def create_jpt(data_1: Union[DataFrame, Series],
               data_2: Union[DataFrame, Series],
               prob_1_name: str, prob_2_name: str,
               prob_1_order: List[str], prob_2_order: List[str]) -> DataFrame:
    """
    Return a joint probability table.

    :param data_1: The DataFrame or Series containing the data for the first
                   distribution.
    :param data_2: The DataFrame or Series containing the data for the second
                   distribution.
    :param prob_1_name: The name of the first question or attribute to find
                        probability of.
    :param prob_2_name: The name of the second question or attribute to find
                        probability of.
    :param prob_1_order: List of labels to order the probability values.
    :param prob_2_order: List of labels to order the conditioning values.
    :return: DataFrame of joint probabilities with Index of `prob_1` and columns
             of `prob_2`.
    """
    if prob_1_name == prob_2_name:
        raise ValueError('prob_1_name must be different to prob_2_name')
    jp_table = count_coincidences(
        data_1=data_1, data_2=data_2,
        column_1=prob_1_name, column_2=prob_2_name,
        column_1_order=prob_1_order, column_2_order=prob_2_order
    )
    jp_table = jp_table / jp_table.sum().sum()

    return jp_table


def create_jct(data_1: Union[DataFrame, Series],
               data_2: Union[DataFrame, Series],
               count_1_name: str, count_2_name: str,
               count_1_order: List[str], count_2_order: List[str]) -> DataFrame:
    """
    Return a joint count table.

    :param data_1: The DataFrame or Series containing the data for the first
                   distribution.
    :param data_2: The DataFrame or Series containing the data for the second
                   distribution.
    :param count_1_name: The name of the first question or attribute to find
                         probability of.
    :param count_2_name: The name of the second question or attribute to find
                         probability of.
    :param count_1_order: List of labels to order the count values.
    :param count_2_order: List of labels to order the count values.
    :return: DataFrame of joint counts with Index of `count_1_order` and columns
             of `count_2_order`.
    """
    if count_1_name == count_2_name:
        raise ValueError('prob_1_name must be different to prob_2_name')
    jc_table = count_coincidences(
        data_1=data_1, data_2=data_2,
        column_1=count_1_name, column_2=count_2_name,
        column_1_order=count_1_order, column_2_order=count_2_order
    )

    return jc_table
