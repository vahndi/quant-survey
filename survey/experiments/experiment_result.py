from typing import Optional

from matplotlib.axes import Axes
from mpl_format.axes.axis_utils import new_axes
from numpy import linspace
from probability.distributions import BetaBinomial

from survey.respondents.respondent_group import RespondentGroup
from survey.surveys.survey import Survey
from survey.utils.formatting import tab_indent


class ExperimentResult(object):

    def __init__(self, survey: Survey,
                 ctl_group: RespondentGroup, exp_group: RespondentGroup,
                 ctl_dist: BetaBinomial, exp_dist: BetaBinomial):
        """
        Create a new ExperimentResult.

        :param survey: The survey used to run the Experiment.
        :param ctl_group: The definition of the Control Group.
        :param exp_group: The definition of the Experimental Group.
        :param ctl_dist: The Distribution for the Control Group.
        :param exp_dist: The Distribution for the Experimental Group.
        """
        self._survey = survey
        self._ctl_group = ctl_group
        self._exp_group = exp_group
        self._ctl_dist = ctl_dist
        self._exp_dist = exp_dist

    @property
    def ctl_group(self) -> RespondentGroup:
        return self._ctl_group

    @property
    def exp_group(self) -> RespondentGroup:
        return self._exp_group

    @property
    def ctl_dist(self) -> BetaBinomial:
        return self._ctl_dist

    @property
    def exp_dist(self) -> BetaBinomial:
        return self._exp_dist

    @property
    def ctl_mean(self) -> float:
        return self._ctl_dist.posterior().mean()

    @property
    def exp_mean(self) -> float:
        return self._exp_dist.posterior().mean()

    @property
    def effect_mean(self) -> float:
        return (
            self._exp_dist.posterior().mean() -
            self._ctl_dist.posterior().mean()
        )

    def prob_ppd_superior(self, reverse: bool = False) -> float:
        if not reverse:
            return self._exp_dist > self._ctl_dist
        else:
            return self._ctl_dist > self._exp_dist

    def plot_posterior_comparison(self, ax: Optional[Axes] = None) -> Axes:
        """
        Plot a comparison of the posterior parameter distribution of each group.

        :param ax: Optional matplotlib axes to plot on.
        """
        theta = linspace(0, 1, 101)
        ax = ax or new_axes()
        # title
        title_parts = []
        if self._ctl_group.respondent_values == self.exp_group.respondent_values:
            title_parts.append(str(self._ctl_group.respondent_values))
        if self._ctl_group.response_values == self._exp_group.response_values:
            title_parts.append(str(self._ctl_group.response_values))
        title_parts.append('effect_mean: {}' % self.effect_mean)
        title = '\n'.join(title_parts)
        # series labels
        ctl_label_parts = []
        exp_label_parts = []
        if self._ctl_group.respondent_values != self._exp_group.respondent_values:
            ctl_label_parts.append(str(self._ctl_group.respondent_values))
            exp_label_parts.append(str(self._exp_group.respondent_values))
        if self._ctl_group.response_values != self._exp_group.response_values:
            ctl_label_parts.append(str(self._ctl_group.response_values))
            exp_label_parts.append(str(self._exp_group.response_values))
        ctl_label = '; '.join(ctl_label_parts)
        exp_label = '; '.join(exp_label_parts)
        ax.set_title(title)
        self._ctl_dist.posterior().plot(x=theta, color='C1',
                                        label=ctl_label, ax=ax)
        self._exp_dist.posterior().plot(x=theta, color='C2',
                                        label=exp_label, ax=ax)
        return ax

    def __repr__(self):

        return (
            f'ExperimentResult('
            f'\n\tsurvey={self._survey.name},'
            f'\n\tctl_group={tab_indent(str(self._ctl_group))},'
            f'\n\texp_group={tab_indent(str(self._exp_group))}'
            f'\n\tctl_mean={self.ctl_mean:2f},'
            f'\n\texp_mean={self.exp_mean:2f},'
            f'\n\teffect_mean={self.effect_mean:2f},'
            f'\n\tp_superior(exp)={self.prob_ppd_superior():2f}'
            f'\n\tp_superior(ctl)={self.prob_ppd_superior(reverse=True):2f}'
            f'\n)'
        )
