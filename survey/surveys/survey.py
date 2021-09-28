from collections import namedtuple, OrderedDict
from typing import Dict, List, Union, Optional, overload

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from mpl_format.axes.axis_utils import new_axes
from mpl_format.text.text_utils import wrap_text
from numpy.ma import diag
from pandas import DataFrame, Series, concat
from probability.distributions import BetaBinomialConjugate
from seaborn import heatmap

from survey.attributes import CountAttribute
from survey.attributes import PositiveMeasureAttribute
from survey.attributes import RespondentAttribute
from survey.attributes import SingleCategoryAttribute
from survey.custom_types import CategoricalQuestion, Categorical, Numerical
from survey.groups.attribute_groups.attribute_group import AttributeGroup
from survey.groups.question_groups.question_group import QuestionGroup
from survey.questions import CountQuestion
from survey.questions import FreeTextQuestion
from survey.questions import LikertQuestion
from survey.questions import MultiChoiceQuestion
from survey.questions import PositiveMeasureQuestion
from survey.questions import Question
from survey.questions import RankedChoiceQuestion
from survey.questions import SingleChoiceQuestion
from survey.respondents.respondent import Respondent
from survey.utils.misc import listify
from survey.utils.plots import set_cpt_axes_labels, plot_pt, plot_cpd, plot_jpd
from survey.utils.probability.prob_utils import create_cpt, create_jpt

BBProbSuperiorResult = namedtuple(
    'BBProbSuperiorResult',
    ['p_superior', 'experimental_mean', 'control_mean']
)


class Survey(QuestionGroup, AttributeGroup, object):
    """
    Represents a Survey.
    """
    def __init__(
            self, name: str, data: DataFrame,
            questions: List[Question],
            respondents: List[Respondent],
            attributes: List[RespondentAttribute],
            groups: Optional[Dict[str, QuestionGroup]] = None
    ):
        """
        Create a new Survey instance.

        :param data: DataFrame with index of respondents,
                     columns of questions and respondent attributes.
        :param questions: List of survey questions.
        :param respondents: List of survey respondents.
        """
        self._name: str = name
        self._data: DataFrame = data
        self._questions: List[Question] = questions
        self._groups = groups or {}
        self._item_dict = {k: v for k, v in self._groups.items()}
        # add question properties
        for question in self._questions:
            question.survey = self
            self._item_dict[question.name] = question
            try:
                setattr(self, question.name, self.question(question.name))
            except TypeError:
                print(
                    f'Warning - could not set dynamic property for '
                    f'{question}'
                )
            try:
                question.data = self._data[question.name]
            except TypeError:
                print(f'Warning - could not set data for {question}')
        self._respondents: List[Respondent] = respondents
        self._attributes: List[RespondentAttribute] = attributes
        # add attribute properties
        for attribute in self._attributes:
            attribute.survey = self
            self._item_dict[attribute.name] = attribute
            try:
                setattr(self, attribute.name, self.attribute(attribute.name))
            except:
                print(
                    f'Warning - could not set dynamic property for '
                    f'{attribute}'
                )
            try:
                attribute.data = self._data[attribute.name]
            except:
                print(f'Warning - could not set data for {attribute}')
        # add group properties
        for name, group in self._groups.items():
            try:
                setattr(self, name, group)
            except:
                print(f'Warning - could not set dynamic group for {group}')

    def question(self, name: str) -> Optional[Question]:
        """
        Return the Question with the given name.

        :param name: Name of the question to return.
        """
        try:
            return [q for q in self._questions if q.name == name][0]
        except IndexError:
            return None

    @property
    def name(self) -> str:
        """
        Return the name of the Survey.
        """
        return self._name

    @property
    def data(self) -> DataFrame:
        return self._data

    # region respondents

    @property
    def respondents(self) -> List[Respondent]:
        """
        Return a list of all the Respondents in the Survey.
        """
        return self._respondents

    @overload
    def find_respondents(
            self, question: Question, answers: Union[str, List[str]]
    ) -> List[Respondent]:
        pass

    @overload
    def find_respondents(
            self, filter_category: Union[str, Categorical],
            filter_values: Union[str, List[str]]
    ) -> List[Respondent]:
        pass

    @overload
    def find_respondents(
            self, question: Question, answers: Union[str, List[str]],
            filter_category: Union[str, Categorical],
            filter_values: Union[str, List[str]]
    ) -> List[Respondent]:
        pass

    def find_respondents(
            self, question: Question = None,
            answers: Union[str, List[str]] = None,
            filter_category: Union[str, Categorical] = None,
            filter_values: Union[str, List[str]] = None
    ) -> List[Respondent]:
        """
        Find respondents matching the given criteria.

        :param question: Question asked.
        :param answers: Allowed answer(s) given.
        :param filter_category: Attribute of the respondents.
        :param filter_values: Allowed values.
        """
        if (
                None in (question, answers) and
                None in (filter_category, filter_values)
        ):
            raise ValueError(
                'Must give question and answers or '
                'filter_category and filter_values'
            )
        data = self._data
        # filter by answer(s)
        if None not in (question, answers):
            answers = listify(answers)
            question_name = self._find_name(question)
            data = data.loc[
                data[question_name].isin(answers)
            ]
        # filter by attribute values
        if None not in (filter_category, filter_values):
            filter_values = listify(filter_values)
            attribute_name = self._find_name(filter_category)
            data = data.loc[
                data[attribute_name].isin(filter_values)
            ]
        # return respondents
        return [r for r in self._respondents
                if r.respondent_id in data.index]

    def respondent_responses(self, respondent: Union[Respondent, str],
                             questions: List[Question] = None,
                             drop_nans: bool = True) -> Series:
        """
        Return the value of the Attribute for each Respondent in the Survey.

        :param respondent: The respondent to return responses for.
        :param questions: Optional list of Questions to filter responses to.
        :param drop_nans: Whether to drop null responses.
        """
        respondent_id = (
            respondent.respondent_id if isinstance(respondent, Respondent)
            else respondent
        )
        responses = self._data.loc[respondent_id, :]
        if questions is not None:
            responses = responses[[q.name for q in questions]]
        if drop_nans:
            responses = responses.dropna()

        return responses

    @property
    def num_respondents(self) -> int:

        return len(self._data)

    # endregion

    # region groups

    @property
    def questions(self) -> QuestionGroup:

        return QuestionGroup(OrderedDict([
            (question.name, question)
            for question in self._questions
        ]))

    @property
    def attributes(self) -> AttributeGroup:

        return AttributeGroup(OrderedDict([
            (attribute.name, attribute)
            for attribute in self._attributes
        ]))

    def group(self, name: str) -> Optional[QuestionGroup]:

        if name in self._groups.keys():
            return self._groups[name]
        return None

    # endregion

    # region responses

    def response_combination_counts(
            self, single_choice: bool = True,
            likert: bool = True,
            multi_choice: bool = True
    ) -> Series:
        """
        Return the count of each unique combination of Responses from
        Survey Respondents.
        """
        # build question list
        questions = []
        if single_choice:
            questions += self.single_choice_question_names
        if likert:
            questions += self.likert_question_names
        if multi_choice:
            questions += self.multi_choice_question_names
        # return combination counts
        return (
            self._data[questions]
                .groupby(questions)
                .size().reset_index()
                .rename(columns={0: 'count'})
        )

    def count_responses(
            self, question: Question, answers: List[str] = None,
            condition_category: Optional[CategoricalQuestion] = None,
            condition_values: Optional[List[str]] = None
    ) -> int:
        """
        Return the number of matching responses to a question.

        :param question: The question to count responses to.
        :param answers: Answer(s) to include in the count.
        :param condition_category: Optional attribute or question to restrict
                                   respondent count with.
        :param condition_values: List of values or answers to use to restrict
                                   respondent count.
        """
        question_name = question.name
        data = self._data.dropna(subset=[question_name])

        if answers is not None:
            if type(answers) is str:
                answers = [answers]
            data = data.loc[(data[question_name].isin(answers))]
        if condition_category is not None and condition_values is not None:
            if type(condition_values) is str:
                condition_values = [condition_values]
            data = data.loc[
                data[condition_category.name].isin(condition_values)
            ]

        return len(data)

    def grouped_word_frequencies(
            self, cat_question: CategoricalQuestion,
            text_question: FreeTextQuestion
    ) -> Dict[str, Series]:
        """
        Calculate the frequency of each word normalized to
        the size of the categorical response value group.
        """
        cat_top_words = {}
        for cat_name in cat_question.category_names:
            respondents = self.find_respondents(question=cat_question,
                                                answers=cat_name)
            responses = self.question_responses(text_question, respondents)
            counts = text_question.word_counts(data=responses)
            cat_top_words[cat_name] = counts.div(len(responses))

        return cat_top_words

    # endregion

    # region probability

    def cpt(self, probability: Union[str, Categorical],
            condition: Union[str, Categorical]) -> DataFrame:
        """
        Return a conditional probability table of 2 Categorical items.

        :param probability: The question or attribute to find probability of.
        :param condition: The question or attribute to condition on.
        :return: DataFrame of conditional probabilities with Index of
                 `condition` and columns of `probability`.
        """
        # find ordering
        prob = self._find_categorical_item(probability)
        cond = self._find_categorical_item(condition)
        return create_cpt(
            prob_data=prob, cond_data=cond,
            prob_name=prob.name, cond_name=cond.name,
            prob_order=prob.categories, cond_order=cond.categories
        )

    def jpt(self, prob_1: Union[str, Categorical],
            prob_2: Union[str, Categorical]) -> DataFrame:
        """
        Return a joint probability table of 2 Categorical items.

        :param prob_1: The question or attribute to find probability of.
        :param prob_2: The question or attribute to condition on.
        :return: DataFrame of conditional probabilities with Index of
                 `condition` and columns of `probability`.
        """
        # find ordering
        p1 = self._find_categorical_item(prob_1)
        p2 = self._find_categorical_item(prob_2)
        return create_jpt(
            data_1=p1.data, data_2=p2.data,
            prob_1_name=p1.name, prob_2_name=p2.name,
            prob_1_order=p1.categories, prob_2_order=p2.categories
        )

    def prob_superior(
            self,
            question: CategoricalQuestion,
            attribute: SingleCategoryAttribute,
            exp_attr_values: List[str], exp_answers: List[str],
            ctl_attr_values: List[str], ctl_answers: List[str]
    ) -> BBProbSuperiorResult:
        """
        Calculate the probability that the number of responses from the
        experimental group in `exp_answers` is significantly higher than the
        number of responses from the control group in `ctl_answers`.

        N.B. to assess the effect of respondent attributes, `exp_answers` and
        `ctl_answers` should be identical.

        :param question: The question to consider.
        :param attribute: The attribute to use.
        :param exp_attr_values: The attribute values of the experimental group.
        :param exp_answers: The answers to count in the experimental group.
        :param ctl_attr_values: The attribute values of the control group.
        :param ctl_answers: The answers to count in the control group.
        """
        # find n and k for experimental respondent and answer group
        n_exp = self.count_responses(question=question,
                                     condition_category=attribute,
                                     condition_values=exp_attr_values)
        k_exp = self.count_responses(question=question, answers=exp_answers,
                                     condition_category=attribute,
                                     condition_values=exp_attr_values)
        # find n and k for control respondent and answer group
        n_ctl = self.count_responses(question=question,
                                     condition_category=attribute,
                                     condition_values=ctl_attr_values)
        k_ctl = self.count_responses(question=question, answers=ctl_answers,
                                     condition_category=attribute,
                                     condition_values=ctl_attr_values)
        # create beta-binomial distribution for each group
        bb_exp = BetaBinomialConjugate(alpha=1, beta=1, n=n_exp, m=k_exp)
        bb_ctl = BetaBinomialConjugate(alpha=1, beta=1, n=n_ctl, m=k_ctl)
        # calculate probability of superiority of test group
        p_superior = bb_exp > bb_ctl

        return BBProbSuperiorResult(
            p_superior=p_superior,
            experimental_mean=bb_exp.posterior().mean(),
            control_mean=bb_ctl.posterior().mean()
        )

    # endregion

    # region plots

    def plot_distribution(
            self, item: Union[str, RespondentAttribute, Question],
            transpose: bool = False, ax: Optional[Axes] = None
    ) -> Axes:
        """
        Plot distribution of answers to a question or values of an attribute.

        :param item: The question or attribute to plot the distribution of.
        :param transpose: Whether to transpose the labels to the y-axis.
        :param ax: Optional matplotlib axes to plot on.
        """
        item = self._find_item(item)
        ax = ax or new_axes()
        item.plot_distribution(transpose=transpose, ax=ax)
        # find the item if the name was passed

        if isinstance(item, str):
            item = self._find_item(item)
        # plot the distribution if the item is valid
        if (
                isinstance(item, RespondentAttribute) or
                isinstance(item, Question)
        ):
            item.plot_distribution(transpose=transpose, ax=ax)
            return ax
        else:
            raise TypeError('Cannot plot this kind of question or attribute.')

    def plot_cpt(self, probability: Union[str, Categorical],
                 condition: Union[str, Categorical],
                 **kwargs) -> Axes:
        """
        Plot a conditional probability table.

        :param probability: The question or attribute to find probability of.
        :param condition: The question or attribute to condition on.
        """
        # calculate create_cpt and fix labels
        cpt = self.cpt(probability, condition)
        if 'transpose' not in kwargs.keys():
            kwargs['transpose'] = False
        if 'var_sep' not in kwargs:
            kwargs['var_sep'] = '|'
        ax = plot_pt(pt=cpt, **kwargs)
        return ax

    def plot_jpt(self, prob_1: Union[str, Categorical],
                 prob_2: Union[str, Categorical],
                 **kwargs) -> Axes:
        """
        Plot a joint probability table.

        :param prob_1: The question or attribute to find probability of.
        :param prob_2: The question or attribute to condition on.
        :param kwargs: See survey.utils.plots.plot_pt.
        """
        # calculate create_cpt and fix labels
        jpt = self.jpt(prob_1, prob_2)
        if 'var_sep' not in kwargs:
            kwargs['var_sep'] = ','
        ax = plot_pt(pt=jpt, **kwargs)
        return ax

    def _plot_pts(self, probs_2: List[Union[str, Categorical]],
                  probs_1: List[Union[str, Categorical]],
                  transpose: bool = True,
                  dividers: bool = True,
                  as_percent: bool = True, precision: int = 0,
                  fig_size=(16, 9), conditional: bool = True) -> Axes:
        """
        Plot conditional probability tables for each pair of items in
        `probabilities` and `conditions`.

        :param probs_2: The questions or attributes to find probability of.
        :param probs_1: The questions or attributes to condition on.
        :param transpose: Set to True to put `conditions` on x-axis.
        :param dividers: Whether to show dividing lines between each condition.
        :param as_percent: Whether to show probabilities as a percentage.
        :param precision: Number of decimal places to display values.
        :param fig_size: Size of the figure to plot on.
        """
        num_probs_1 = len(probs_1)
        num_probs_2 = len(probs_2)
        if transpose:
            n_rows = num_probs_2
            n_cols = num_probs_1
        else:
            n_rows = num_probs_1
            n_cols = num_probs_2
        fig, ax = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=fig_size)
        for p1, prob_1 in enumerate(probs_1):
            for p2, prob_2 in enumerate(probs_2):
                if transpose:
                    axes = (
                        ax[p2, p1] if n_rows > 1 and n_cols > 1
                        else ax[p2] if n_rows > 1
                        else ax[p1] if n_cols > 1
                        else ax
                    )
                    x_labels = p2 == num_probs_2 - 1
                    y_labels = p1 == 0
                else:
                    axes = (
                        ax[p1, p2] if n_rows > 1 and n_cols > 1
                        else ax[p1] if n_rows > 1
                        else ax[p2] if n_cols > 1
                        else ax
                    )
                    x_labels = p1 == num_probs_1 - 1
                    y_labels = p2 == 0
                prob_1_name = self._find_categorical_name(prob_1)
                prob_2_name = self._find_categorical_name(prob_2)
                if prob_1_name != prob_2_name:
                    if conditional:
                        self.plot_cpt(
                            probability=prob_2, condition=prob_1,
                            transpose=transpose,
                            set_title=False, ax=axes, cbar=False,
                            x_tick_labels=x_labels, y_tick_labels=y_labels,
                            x_label=x_labels, y_label=y_labels,
                            dividers=dividers,
                            as_percent=as_percent, precision=precision
                        )
                    else:
                        self.plot_jpt(
                            prob_1=prob_1, prob_2=prob_2,
                            transpose=transpose,
                            set_title=False, ax=axes, cbar=False,
                            x_tick_labels=x_labels, y_tick_labels=y_labels,
                            x_label=x_labels, y_label=y_labels,
                            dividers=dividers,
                            as_percent=as_percent, precision=precision
                        )
                else:
                    prob_1_name, cond_order = self._find_name_and_values(prob_1)
                    counts = self._data[prob_1_name].value_counts().reindex(
                        cond_order
                    )
                    matrix = diag(counts.values)
                    heatmap(matrix, ax=axes, cmap='Blues',
                            annot=True, fmt='0.0f', cbar=False)
                    axes.invert_yaxis()
                    set_cpt_axes_labels(ax=axes,
                                        x_label=x_labels, y_label=y_labels,
                                        cond_name=prob_1_name,
                                        prob_name=prob_2_name,
                                        transpose=transpose)
                    if x_labels:
                        axes.set_xticklabels(wrap_text(counts.index))
                    else:
                        axes.set_xticklabels([])
                    if y_labels:
                        axes.set_yticklabels(wrap_text(counts.index))
                    else:
                        axes.set_yticklabels([])
        return ax

    def plot_cpts(self, probabilities: List[Union[str, Categorical]],
                  conditions: List[Union[str, Categorical]],
                  transpose: bool = True,
                  dividers: bool = True,
                  as_percent: bool = True, precision: int = 0,
                  fig_size=(16, 9)) -> Axes:
        """
        Plot conditional probability tables for each pair of items in
        `probabilities` and `conditions`.

        :param probabilities: Questions or attributes to find probability of.
        :param conditions: Questions or attributes to condition on.
        :param transpose: Set to True to put `conditions` on x-axis.
        :param dividers: Whether to show dividing lines between each condition.
        :param as_percent: Whether to show probabilities as a percentage.
        :param precision: Number of decimal places to display values.
        :param fig_size: Size of the figure to plot on.
        """
        return self._plot_pts(
            probs_2=probabilities, probs_1=conditions,
            transpose=transpose, dividers=dividers,
            as_percent=as_percent, precision=precision,
            fig_size=fig_size, conditional=True
        )
    
    def plot_jpts(self, probs_1: List[Union[str, Categorical]],
                  probs_2: List[Union[str, Categorical]],
                  transpose: bool = True,
                  dividers: bool = False,
                  as_percent: bool = True, precision: int = 0,
                  fig_size=(16, 9)) -> Axes:
        """
        Plot conditional probability tables for each pair of items in
        `probabilities` and `conditions`.

        :param probs_1: First questions or attributes to find probability of.
        :param probs_2: Second questions or attributes to find probability of.
        :param transpose: Set to True to put `conditions` on x-axis.
        :param dividers: Whether to show dividing lines between each condition.
        :param as_percent: Whether to show probabilities as a percentage.
        :param precision: Number of decimal places to display values.
        :param fig_size: Size of the figure to plot on.
        """
        return self._plot_pts(
            probs_2=probs_2, probs_1=probs_1,
            transpose=transpose, dividers=dividers,
            as_percent=as_percent, precision=precision,
            fig_size=fig_size, conditional=False
        )

    def plot_cpd(self, probability: Union[str, Numerical],
                 condition: Union[str, Numerical],
                 transpose: bool = False,
                 set_title: bool = True, legend: bool = True,
                 x_label: bool = True, y_label: bool = True,
                 x_tick_labels: bool = True, y_tick_labels: bool = True,
                 ax: Optional[Axes] = None) -> Axes:
        """
        Plot a conditional probability distribution as a kde for each condition
        category.

        :param probability: The question or attribute to find probability of.
        :param condition: The question or attribute to condition on.
        :param transpose: Set to True to put values along y-axis.
        :param set_title: Whether to add a title to the plot.
        :param legend: Whether to show a legend or not.
        :param x_label: Whether to show the default label on the x-axis or not,
                        or string of text for the label.
        :param y_label: Whether to show the default label on the y-axis or not,
                        or string of text for the label.
        :param x_tick_labels: Whether to show labels on the ticks on the x-axis.
        :param y_tick_labels: Whether to show labels on the ticks on the y-axis.
        :param ax: Optional matplotlib axes to plot on.
        """
        prob_name = self._find_numerical_name(probability)
        cond_name = self._find_categorical_name(condition)
        ax = plot_cpd(
            survey_data=self._data, probability=prob_name, condition=cond_name,
            transpose=transpose, set_title=set_title, legend=legend,
            x_label=x_label, y_label=y_label,
            x_tick_labels=x_tick_labels, y_tick_labels=y_tick_labels,
            ax=ax
        )
        return ax

    def plot_cpds(self, probabilities: List[Union[str, Numerical]],
                  conditions: List[Union[str, Numerical]],
                  transpose: bool = False, fig_size=(16, 9)) -> Axes:
        """
        Plot conditional probability distributions for each pair of items in
        `probabilities` and `conditions`.

        :param probabilities: Questions or attributes to find probability of.
        :param conditions: Questions or attributes to condition on.
        :param transpose: Set to True to put `conditions` on x-axis.
        :param fig_size: Size of the figure to plot on.
        """
        num_conditions = len(conditions)
        num_probabilities = len(probabilities)
        if transpose:
            n_rows = num_probabilities + 1
            n_cols = num_conditions
        else:
            n_rows = num_conditions
            n_cols = num_probabilities + 1

        fig, ax = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=fig_size)
        for c, condition in enumerate(conditions):
            for p, probability in enumerate(probabilities):
                if transpose:
                    axes = ax[p, c]
                    x_labels = p == num_probabilities - 1
                    y_labels = c == 0
                else:
                    axes = ax[c, p]
                    x_labels = c == num_conditions - 1
                    y_labels = p == 0
                condition = self._find_categorical_item(condition)
                probability = self._find_numerical_item(probability)
                if condition.name != probability.name:
                    self.plot_cpd(
                        probability=probability, condition=condition,
                        transpose=transpose,
                        set_title=False, legend=False,
                        x_tick_labels=x_labels, y_tick_labels=y_labels,
                        x_label=x_labels, y_label=y_labels, ax=axes
                    )
        for c, condition in enumerate(conditions):
            if transpose:
                axes = ax[num_probabilities, c]
            else:
                axes = ax[c, num_probabilities]
            cond_names = self._data[condition.name].unique()
            for cond_name in cond_names:
                axes.plot([], [], label=cond_name)
            axes.legend(title=condition.name, loc=2)
            axes.set_xticks([])
            axes.set_yticks([])
            axes.set_frame_on(False)

        return ax

    def plot_crtf(self, categorical: Union[str, Categorical],
                  free_text: Union[str, FreeTextQuestion],
                  top_n: int = 50, transpose: bool = True,
                  ax: Optional[Axes] = None) -> Axes:
        """
        Plot a heatmap of the relative term frequency of top words given by
        respondents to a free text question, grouped according to the their
        response to a categorical question.

        Relative means relative to the number of respondents in the group who
        gave the same response.

        :param categorical: The categorical response or attribute to group by.
        :param free_text: The FreeTextQuestion to calculate relative word
                          frequencies from.
        :param top_n: The number of the most frequent words to use.
        :param transpose: `True` to put terms along the x-axis, `False` for
                          y-axis.
        :param ax: Optional matplotlib axes to plot on.
        """
        # find categorical attribute or question
        categorical = self._find_categorical_item(categorical)
        cat_question = self.categorical_question(categorical.name)
        # find free text question
        if type(free_text) not in (str, FreeTextQuestion):
            raise TypeError('free_text must be of type str or FreeTextQuestion')
        if type(free_text) is str:
            free_text = self.free_text_question(free_text)

        cat_top_words = self.grouped_word_frequencies(
            cat_question=cat_question, text_question=free_text
        )
        all_words = (
            concat([
                value for value in cat_top_words.values()
            ]).sort_values(ascending=False)
            if cat_top_words.values()
            else Series()
        )
        all_words = all_words.groupby(all_words.index).max().sort_values(
            ascending=False
        )[: top_n]
        data = {}
        for cat, top_words in cat_top_words.items():
            data[cat] = top_words.reindex(all_words.index)
        if len(data) == 0:
            print(f'warning - no data for plot_crtf heatmap using '
                  f'cat={categorical.name} and text={free_text.name}')
            return ax
        data = DataFrame(data)
        data.columns = wrap_text(data.columns)
        if transpose:
            data = data.T
        ax = ax or new_axes()
        heatmap(data, linewidths=1, linecolor='#bbbbbb', ax=ax)
        if transpose:
            ax.set_xlabel('Relative Word Frequency')
            ax.set_ylabel('Response')
        else:
            ax.set_ylabel('Relative Word Frequency')
            ax.set_xlabel('Response')
        ax.set_title(f'Relative Word Frequencies for '
                     f'{free_text.name} given Response to {categorical.name}')

        return ax

    def plot_jpd(self, prob_1: str, prob_2: str,
                 kind: str = 'kde',
                 set_title: bool = True, legend: bool = False,
                 transpose: bool = False,
                 x_label: bool = True, y_label: bool = True,
                 x_tick_labels: bool = True, y_tick_labels: bool = True,
                 ax: Optional[Axes] = None) -> Axes:
        """
        Plot a joint probability distribution of 2 columns.

        :param prob_1: The first marginal probability distribution.
        :param prob_2: The second marginal probability distribution.
        :param kind: 'kde' or 'scatter'.
        :param transpose: Set to True to put prob_1 along the y-axis.
        :param set_title: Whether to add a title to the plot.
        :param legend: Whether to show a legend or not.
        :param x_label: Whether to show the default label on the x-axis or not,
                        or string of text for the label.
        :param y_label: Whether to show the default label on the y-axis or not,
                        or string of text for the label.
        :param x_tick_labels: Whether to show labels on the ticks on the x-axis.
        :param y_tick_labels: Whether to show labels on the ticks on the y-axis.
        :param ax: Optional matplotlib axes to plot on.
        """
        prob_1_name = self._find_numerical_name(prob_1)
        prob_2_name = self._find_numerical_name(prob_2)
        ax = plot_jpd(survey_data=self._data,
                      prob_1=prob_1_name, prob_2=prob_2_name,
                      kind=kind,
                      set_title=set_title, legend=legend, transpose=transpose,
                      x_label=x_label, y_label=y_label,
                      x_tick_labels=x_tick_labels, y_tick_labels=y_tick_labels,
                      ax=ax)
        return ax

    def plot_jpds(self, probs_1: List[Union[str, Numerical]],
                  probs_2: List[Union[str, Numerical]],
                  transpose, fig_size=(16, 9)) -> Axes:
        """
        Plot joint probability distributions for each pair of items in `probs_1`
        and `probs_2`.

        :param probs_1: The questions or attributes to find probability of.
        :param probs_2: The questions or attributes to condition on.
        :param transpose: Set to True to put `conditions` on x-axis.
        :param fig_size: Size of the figure to plot on.
        """
        num_probs_1 = len(probs_1)
        num_probs_2 = len(probs_2)
        if transpose:
            n_rows = num_probs_1
            n_cols = num_probs_2
        else:
            n_rows = num_probs_2
            n_cols = num_probs_1
        fig, ax = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=fig_size)
        for p1, prob_1 in enumerate(probs_1):
            for p2, prob_2 in enumerate(probs_2):
                if transpose:
                    axes = ax[p1, p2]
                    x_labels = p1 == num_probs_1 - 1
                    y_labels = p2 == 0
                else:
                    axes = ax[p2, p1]
                    x_labels = p2 == num_probs_2 - 1
                    y_labels = p1 == 0
                prob_1_name = prob_1.name
                prob_2_name = prob_2.name
                if prob_2_name != prob_1_name:
                    self.plot_jpd(
                        prob_1=prob_1_name, prob_2=prob_2_name,
                        set_title=False, legend=False,
                        x_label=x_labels, y_label=y_labels,
                        x_tick_labels=x_labels, y_tick_labels=y_labels,
                        ax=axes
                    )
                else:
                    dist_data = self._data[prob_1_name].dropna()
                    axes.scatter(x=dist_data, y=dist_data, alpha=0.1)
                    # label axes
                    if not x_labels:
                        axes.set_xlabel('')
                        axes.set_xticklabels([])
                    else:
                        axes.set_xlabel(wrap_text(prob_1_name))
                    if not y_labels:
                        axes.set_ylabel('')
                        axes.set_yticklabels([])
                    else:
                        axes.set_ylabel(wrap_text(prob_1_name))
                    #  set axis ranges
                    if 0 <= dist_data.min() < dist_data.max() / 10:
                        axes.set_xlim(0, axes.get_xlim()[1])
                        axes.set_ylim(0, axes.get_ylim()[1])

        return ax

    # endregion

    # region utils

    def get_data(
            self, item: Union[str, Question, RespondentAttribute]
    ) -> Series:
        """
        Return the Series of data for the given item.

        :param item: The item to get data for.
        """
        if isinstance(item, str):
            if item in self._data.columns:
                return self._data[item]
            else:
                raise ValueError(f'Could not locate item named {item}')
        elif (
                isinstance(item, Question) or
                isinstance(item, RespondentAttribute)
        ):
            item_name = self._find_name(item)
            return self._data[item_name]
        else:
            raise TypeError(
                'item must be of type str, Question or RespondentAttribute'
            )

    def make_question_features(
            self, null_value: str = None, naming: str = '{{name}}: {{choice}}',
            normalize: bool = True, binarize: bool = True
    ) -> DataFrame:
        """
        Return DataFrame of all question features in the Survey
        """
        features = DataFrame()
        for q in self.questions:
            feature = None
            if isinstance(q, SingleChoiceQuestion):
                feature = self.single_choice_question(q.name).make_features(
                    null_value=null_value, naming=naming, binarize=binarize
                )
            if isinstance(q, RankedChoiceQuestion):
                feature = self.ranked_choice_question(q.name).make_features(
                    null_category=null_value, naming=naming, normalize=normalize
                )
            if isinstance(q, PositiveMeasureQuestion):
                feature = self.positive_measure_question(q.name).make_features(
                    normalize=normalize
                )
            if isinstance(q, MultiChoiceQuestion):
                feature = self.multi_choice_question(q.name).make_features(
                    null_value=null_value, naming=naming
                )
            if isinstance(q, LikertQuestion):
                feature = self.likert_question(q.name).make_features(
                    normalize=normalize
                )
            if isinstance(q, FreeTextQuestion):
                continue
            if isinstance(q, CountQuestion):
                feature = self.count_question(q.name).make_features(
                    normalize=normalize
                )
            if feature is not None:
                features = concat([features, feature], axis=1)
        return features

    def make_attribute_features(
            self, null_value: str = None, naming: str = '{{name}}: {{choice}}',
            normalize: bool = True, binarize: bool = True
    ) -> DataFrame:
        """
        Return DataFrame of all question features in the Survey
        """
        features = DataFrame()
        for a in self.attributes:
            feature = None
            if isinstance(a, SingleCategoryAttribute):
                feature = self.single_category_attribute(a.name).make_features(
                    null_value=null_value, naming=naming, binarize=binarize
                )
            if isinstance(a, PositiveMeasureAttribute):
                feature = self.positive_measure_attribute(a.name).make_features(
                    normalize=normalize
                )
            if isinstance(a, CountAttribute):
                feature = self.count_attribute(a.name).make_features(
                    normalize=normalize
                )
            if feature is not None:
                features = concat([features, feature], axis=1)
        return features

    # endregion

    #  region overrides of built-ins

    def __repr__(self):

        return (
            f'Survey('
            f'\n\tquestions={len(self._questions)},'
            f'\n\trespondents={len(self._respondents)},'
            f'\n\tattributes={len(self._attributes)}'
            f'\n)'
        )

    def __getitem__(self, item: str) -> Union[Question,
                                              RespondentAttribute,
                                              QuestionGroup]:
        """
        Return the item with the given name.

        :param item: The item to get data for.
        """
        try:
            return self._item_dict[item]
        except KeyError:
            raise KeyError(f'Error: Item {item} does not exist in Survey.')

    # endregion
