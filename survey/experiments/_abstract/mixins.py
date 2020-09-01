from itertools import product
from pandas import DataFrame
from probability.distributions import BetaBinomial, BetaBinomialConjugate
from tqdm import tqdm
from typing import List, Tuple

from survey import Survey
from survey.attributes import SingleCategoryAttribute
from survey.custom_types import Categorical
from survey.experiments import ExperimentResult
from survey.questions import SingleChoiceQuestion
from survey.respondents import RespondentGroup


class SingleToSingleExperimentMixin(object):

    _survey: Survey
    _dependent: Categorical
    _independent: Categorical
    _dependent_getter: str
    _independent_getter: str
    _dependent_names: str
    _independent_names: str
    _results: List[ExperimentResult]

    def set_values(self, survey: Survey,
                   dependent: Categorical,
                   independent: Categorical):
        """
        Set dependent and independent values for the Experiment.
        """
        if type(dependent) is str:
            dependent = getattr(survey, self._dependent_getter)(dependent)
            if dependent is None:
                raise ValueError(
                    f'Error - {dependent.name} is not a '
                    f'{self._dependent.__name__} in the survey.'
                )
        self._dependent = dependent
        if type(independent) is str:
            independent = getattr(survey, self._independent_getter)(independent)
            if independent is None:
                raise ValueError(
                    f'Error - {independent.name} is not a '
                    f'{self._independent.__name__} in the survey.'
                )
        self._independent = independent

        self._results = []

    def calculate(
            self,
            exp_ind_values: List[str],
            exp_dep_values: List[str],
            ctl_ind_values: List[str],
            ctl_dep_values: List[str]
        ) -> Tuple[BetaBinomial, BetaBinomial]:
        """
        Calculate the probability that the number of responses from the
        experimental group in `exp_answers` is significantly higher than the
        number of responses from the control group in `ctl_answers`.

        N.B. to assess the effect of respondent attributes, `exp_answers` and
        `ctl_answers` should be identical.

        :param exp_ind_values: The answers given by the experimental group to
                               the independent question.
        :param exp_dep_values: The answers to the dependent question to count in
                               the experimental group.
        :param ctl_ind_values: The answers given by the control group to the
                               independent question.
        :param ctl_dep_values: The answers to the dependent question to count in
                               the control group.
        """
        # find n and k for experimental respondent and answer group
        n_exp = self._survey.count_responses(
            question=self._dependent,
            condition_category=self._independent,
            condition_values=exp_ind_values
        )
        k_exp = self._survey.count_responses(
            question=self._dependent, answers=exp_dep_values,
            condition_category=self._independent,
            condition_values=exp_ind_values
        )
        # find n and k for control respondent and answer group
        n_ctl = self._survey.count_responses(
            question=self._dependent,
            condition_category=self._independent,
            condition_values=ctl_ind_values
        )
        k_ctl = self._survey.count_responses(
            question=self._dependent, answers=ctl_dep_values,
            condition_category=self._independent,
            condition_values=ctl_ind_values
        )
        # create beta-binomial distribution for each group
        bb_exp = BetaBinomialConjugate(alpha=1, beta=1, n=n_exp, m=k_exp)
        bb_ctl = BetaBinomialConjugate(alpha=1, beta=1, n=n_ctl, m=k_ctl)
        # calculate probability of superiority of test group
        return bb_ctl, bb_exp

    def run(self, show_progress: bool = True):
        """
        Analyze responses to a question between respondents with different
        values of an attribute. Leads to statements of the form "respondents
        with an attribute value of X are Y%  more likely to answer Z than
        respondents with an attribute value of ~X" e.g. "men are 50% more likely
        to switch plans than women".

        :param show_progress: Whether to show a tqdm progress bar of the
                              calculations.
        """
        self._results = []
        # iterate over groups of respondent independent and dependent answer
        # choices
        iterator = list(product(
            self._independent.group_pairs(ordered=self._independent.ordered),
            self._dependent.group_pairs(ordered=self._dependent.ordered)
        ))
        if show_progress:
            iterator = tqdm(iterator)
        for (
                (answers_ind_exp, answers_ind_ctl),
                (answers_dep_exp, answers_dep_ctl)
        ) in iterator:
            bb_ctl, bb_exp = self.calculate(
                exp_ind_values=answers_ind_exp, exp_dep_values=answers_dep_exp,
                ctl_ind_values=answers_ind_ctl, ctl_dep_values=answers_dep_exp
            )
            # compile result data
            result = ExperimentResult(
                survey=self._survey,
                ctl_group=RespondentGroup(
                    respondent_values={self._independent.name: answers_ind_ctl},
                    response_values={self._dependent.name: answers_dep_exp}
                ),
                exp_group=RespondentGroup(
                    respondent_values={self._independent.name: answers_ind_exp},
                    response_values={self._dependent.name: answers_dep_exp}
                ),
                ctl_dist=bb_ctl,
                exp_dist=bb_exp
            )
            self._results.append(result)

    def results_data(
            self, group_values: bool, join_str: str = ' || '
    ) -> DataFrame:
        """
        Return a DataFrame of the experiment results.

        :param group_values: Whether to group values into single columns rather
                             than creating a boolean column for each value.
        :param join_str: String to join grouped values with.
        """
        ind_name = self._independent.name
        results_list = []

        for result in self._results:

            ind_values_exp = result.exp_group.respondent_values[
                self._independent.name]
            ind_values_ctl = result.ctl_group.respondent_values[
                self._independent.name]
            dep_values_exp = result.exp_group.response_values[
                self._dependent.name]
            dep_values_ctl = [val for val in self._dependent.category_names
                              if val not in dep_values_exp]
            if group_values:
                result_dict = dict(
                    survey_name=self._survey.name,
                    survey_question=self._dependent.name,
                    attribute_name=self._independent.name
                )
                result_dict[
                    f'{self._independent_names}_exp'
                ] = join_str.join(ind_values_exp)
                result_dict[
                    f'{self._independent_names}_ctl'
                ] = join_str.join(ind_values_ctl)
                result_dict[
                    f'{self._dependent_names}_exp'
                ] = join_str.join(dep_values_exp)
                result_dict[
                    f'{self._dependent_names}_ctl'
                ] = join_str.join(dep_values_ctl)
                result_dict['p_superior'] = result.prob_ppd_superior()
                result_dict['effect_mean'] = result.effect_mean
                result_dict['exp_mean'] = result.exp_mean
                result_dict['ctl_mean'] = result.ctl_mean
            else:
                result_dict = {
                    ('survey', 'name'): self._survey.name,
                    ('survey', 'question'): self._dependent.name,
                }
                for attr in ind_values_exp:
                    result_dict[(ind_name, attr)] = True
                for attr in ind_values_ctl:
                    result_dict[(ind_name, attr)] = False
                for answer in dep_values_exp:
                    result_dict[('answer', answer)] = True
                for answer in dep_values_ctl:
                    result_dict[('answer', answer)] = False
                result_dict[
                    ('result', 'p_superior')
                ] = result.prob_ppd_superior()
                result_dict[('result', 'effect_mean')] = result.effect_mean
                result_dict[('result', 'exp_mean')] = result.exp_mean
                result_dict[('result', 'ctl_mean')] = result.ctl_mean

            results_list.append(result_dict)

        # compile respondent category results
        if group_values:
            results = DataFrame(results_list)[
                ['survey_name', 'survey_question', 'attribute_name'] +
                ['ind_answers_exp', 'ind_answers_ctl'] +
                ['dep_answers_exp', 'dep_answers_ctl'] +
                ['p_superior', 'effect_mean', 'exp_mean', 'ctl_mean']
                ]
        else:
            results = DataFrame(results_list)[
                [('survey', 'name'), ('survey', 'question')] +
                [(ind_name, ind_answer)
                 for ind_answer in self._independent.category_names] +
                [('answer', answer)
                 for answer in self._dependent.category_names] +
                [('result', 'p_superior'), ('result', 'effect_mean'),
                 ('result', 'exp_mean'), ('result', 'ctl_mean')]
                ]

        return results


class SingleChoiceQuestionDependentMixin(object):
    _dependent_type = SingleChoiceQuestion
    _dependent_getter = 'single_choice_question'
    _dependent_names = 'dep_answers'


class SingleChoiceQuestionIndependentMixin(object):
    _independent_type = SingleChoiceQuestion
    _independent_getter = 'single_choice_question'
    _independent_names = 'ind_answers'


class SingleCategoryAttributeDependentMixin(object):
    _dependent_type = SingleCategoryAttribute
    _dependent_getter = 'categorical_attribute'
    _dependent_names = 'dep_attr_vals'


class SingleCategoryAttributeIndependentMixin(object):
    _independent_type = SingleCategoryAttribute
    _independent_getter = 'categorical_attribute'
    _independent_names = 'ind_attr_vals'
