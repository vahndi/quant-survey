from matplotlib.axes import Axes
from mpl_format.axes.axis_utils import new_axes
from typing import List, Optional

from survey.experiments.experiment_result import ExperimentResult
from survey.respondents.respondent_group import RespondentGroup


class Experiment(object):

    _results: List[ExperimentResult]

    @property
    def results(self) -> List[ExperimentResult]:
        """
        Return the calculated experiment results.
        """
        return self._results

    def result(self, ctl_group: RespondentGroup,
               exp_group: RespondentGroup) -> Optional[ExperimentResult]:
        """
        Return the result for the given combination of control and experimental
        groups.

        :param ctl_group: Control Respondent Group.
        :param exp_group: Experimental Respondent Group.
        """
        for result in self._results:
            if result.ctl_group == ctl_group and result.exp_group == exp_group:
                return result
        return None

    def results_data(self, group_values: bool):

        raise NotImplementedError

    def plot_results(
            self, x: str = 'effect_mean', y: str = 'p_superior',
            split_by: str = 'answers_given', ax: Optional[Axes] = None
    ) -> Axes:
        """
        Create a scatter plot of the experimental results.

        :param x: Name of the attribute for the x-axis.
        :param y: Name of the attribute for the y-axis.
        :param split_by: Name of the attribute to split into different series.
        :param ax: Optional matplotlib axes to plot on.
        """
        data = self.results_data(group_values=True)
        ax = ax or new_axes()
        for split_val in data[split_by].unique():
            split_data = data.loc[data[split_by] == split_val]
            ax.scatter(split_data[x], split_data[y], label=split_val)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.legend()

        return ax
