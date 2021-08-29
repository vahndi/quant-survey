from itertools import product
from typing import List, Tuple, Optional

from matplotlib.axes import Axes
from pandas import Series, DataFrame
from probability.distributions import BetaBinomialConjugate

from survey.utils.data_frames import count_coincidences
from survey.utils.plots import plot_pt
from survey.utils.probability.prob_utils import create_jpt, create_cpt, \
    create_jct


class SingleCategoryPTMixin(object):

    data: Series
    category_names: List[str]
    name: str

    def _draw_significance_values(
            self, other: 'SingleCategoryPTMixin',
            sig_colors: Tuple[str, str],
            sig_values: Tuple[float, float],
            transpose: bool,
            ax: Axes
    ):

        counts = count_coincidences(
            data_1=self.data, data_2=other.data,
            column_1=self.name, column_2=other.name,
            column_1_order=self.category_names,
            column_2_order=other.category_names
        )
        # calculate p(X=x,Y=y) > mean(p(X=~x, Y=~y)) for each x and y
        n_total = counts.sum().sum()  # total number of coincidences
        results = []
        for cat_1, cat_2 in product(self.category_names,
                                    other.category_names):
            m_event = counts.loc[cat_2, cat_1]  # coincidences with value combo
            m_any = (
                (n_total - m_event) /  # coincidences not with value combo
                (len(self.category_names) *
                 len(other.category_names) - 1)  # number of other value combos
            )  # average of all other coincidence counts
            results.append({
                self.name: cat_1,
                other.name: cat_2,
                'p': (
                        BetaBinomialConjugate(
                            alpha=1, beta=1, n=n_total, k=m_event
                        ).posterior() >
                        BetaBinomialConjugate(
                            alpha=1, beta=1, n=n_total, k=m_any
                        ).posterior()
                )
            })
        results_data = DataFrame(results)
        # define plot offsets
        min_add = 0.05
        max_add = 0.95
        line_width = 2
        # draw significance rectangles
        for _, row in results_data.iterrows():
            color = None
            if row['p'] >= sig_values[0]:
                color = sig_colors[0]
            elif row['p'] < sig_values[1]:
                color = sig_colors[1]
            if color is None:
                continue
            if not transpose:
                x = self.category_names.index(row[self.name])
                y = other.category_names.index(row[other.name])
            else:
                y = self.category_names.index(row[self.name])
                x = other.category_names.index(row[other.name])

            ax.plot([x + min_add, x + max_add], [y + min_add, y + min_add],
                    color, linewidth=line_width)
            ax.plot([x + min_add, x + max_add], [y + max_add, y + max_add],
                    color, linewidth=line_width)
            ax.plot([x + min_add, x + min_add], [y + min_add, y + max_add],
                    color, linewidth=line_width)
            ax.plot([x + max_add, x + max_add], [y + min_add, y + max_add],
                    color, linewidth=line_width)

    def plot_jpt(self, other: 'SingleCategoryPTMixin',
                 significance: bool = False,
                 sig_colors: Tuple[str, str] = ('#00ff00', '#ff0000'),
                 sig_values: Tuple[float, float] = (0.945, 0.055),
                 **kwargs) -> Axes:
        """
        Plot a joint probability table of self and other.

        :param other: Another SingleCategory to plot against.
        :param significance: Whether to add significance markers to the plot.
                             Equal to p(X=x1,Y=y1) > p(X≠x1, Y≠y1).
        :param sig_colors: Tuple of (high, low) colors for highlighting
                           significance.
        :param sig_values: Tuple of (high, low) values for assessing
                           significance.
        :param kwargs: See utils.plots.plot_pt
        """
        if self.name == other.name:
            raise ValueError('categoricals must have different names')
        if isinstance(other, SingleCategoryPTMixin):
            other_data = other.data
        else:
            # assume multi category
            other_data = other.make_features(naming='{{choice}}')
        # calculate jpt
        jpt = create_jpt(
            data_1=self.data, data_2=other_data,
            prob_1_name=self.name, prob_2_name=other.name,
            prob_1_order=self.category_names,
            prob_2_order=other.category_names
        )
        if 'transpose' not in kwargs.keys():
            kwargs['transpose'] = False
        if 'var_sep' not in kwargs.keys():
            kwargs['var_sep'] = ','
        if 'dividers' not in kwargs.keys():
            kwargs['dividers'] = False
        ax = plot_pt(pt=jpt, **kwargs)

        # draw significance values
        if significance and isinstance(other, SingleCategoryPTMixin):
            self._draw_significance_values(
                other=other,
                sig_colors=sig_colors,
                sig_values=sig_values,
                transpose=kwargs['transpose'],
                ax=ax
            )

        return ax

    def plot_cpt(self,
                 condition: 'SingleCategoryPTMixin',
                 significance: Optional[str] = None,
                 sig_colors: Tuple[str, str] = ('#00ff00', '#ff0000'),
                 sig_values: Tuple[float, float] = (0.945, 0.055),
                 **kwargs) -> Axes:
        """
        Plot a conditional probability table of self and other.

        :param condition: Another SingleCategory to condition on.
        :param significance: One of ['prob', 'cond'].
                            'prob' gives p(X=x1|Y=y1) > p(X≠x1|Y=y1)
                            'cond' gives p(X=x1|Y=y1) > p(X=x1|Y≠y1)
        :param sig_colors: Tuple of (high, low) colors for highlighting
                           significance.
                           Equal to p(X=x1,Y=y1) > p(X≠x1, Y≠y1).
        :param sig_values: Tuple of (high, low) values for assessing
                           significance.
        :param kwargs: See utils.plots.plot_pt
        """
        if self.name == condition.name:
            raise ValueError('categoricals must have different names')
        if isinstance(condition, SingleCategoryPTMixin):
            condition_data = condition.data
        else:
            # assume multi category
            condition_data = condition.make_features(naming='{{choice}}')
        jpt = create_cpt(
            prob_data=self.data, cond_data=condition_data,
            prob_name=self.name, cond_name=condition.name,
            prob_order=self.category_names, cond_order=condition.category_names
        )
        if 'var_sep' not in kwargs.keys():
            kwargs['var_sep'] = '|'
        if not 'transpose' in kwargs.keys():
            kwargs['transpose'] = True
        ax = plot_pt(pt=jpt, **kwargs)

        # draw significance values
        if significance is not None:
            counts = count_coincidences(
                data_1=self.data, data_2=condition_data,
                column_1=self.name, column_2=condition.name,
                column_1_order=self.category_names,
                column_2_order=condition.category_names
            )
            if isinstance(condition, SingleCategoryPTMixin):
                results = []
                if significance == 'prob':
                    for cond_cat in condition.category_names:
                        n_cond = counts.loc[cond_cat].sum()
                        for prob_cat in self.category_names:
                            m_prob_cond = counts.loc[cond_cat, prob_cat]
                            m_any = (
                                (n_cond - m_prob_cond) /
                                (len(self.category_names) - 1)
                            )
                            p = (
                                BetaBinomialConjugate(
                                    alpha=1, beta=1, n=n_cond, k=m_prob_cond
                                ).posterior() > BetaBinomialConjugate(
                                    alpha=1, beta=1, n=n_cond, k=m_any
                                ).posterior()
                            )
                            results.append({
                                self.name: prob_cat,
                                condition.name: cond_cat,
                                'p': p
                            })
                elif significance == 'cond':
                    n = counts.sum().sum()
                    for prob_cat in self.category_names:
                        n_prob = counts[prob_cat].sum()
                        for cond_cat in condition.category_names:
                            n_cond = counts.loc[cond_cat].sum()
                            m_prob_cond = counts.loc[cond_cat, prob_cat]
                            m_any = n_prob - m_prob_cond
                            n_any = n - n_cond
                            p = (
                                BetaBinomialConjugate(
                                    n=n_cond, k=m_prob_cond, alpha=1, beta=1,
                                ).posterior() > BetaBinomialConjugate(
                                    n=n_any, k=m_any, alpha=1, beta=1
                                ).posterior()
                            )
                            results.append({
                                self.name: prob_cat,
                                condition.name: cond_cat,
                                'p': p
                            })
                else:
                    raise ValueError(
                        "significance must be one of ['prob', 'cond']"
                    )

                results_data = DataFrame(results)

            else:
                raise NotImplementedError(
                    'significance not implemented for MultiCategories'
                )

            min_add = 0.1
            max_add = 0.9
            line_width = 2

            for _, row in results_data.iterrows():
                color = None
                if row['p'] >= sig_values[0]:
                    color = sig_colors[0]
                elif row['p'] < sig_values[1]:
                    color = sig_colors[1]
                if color is None:
                    continue
                if not kwargs['transpose']:
                    x = self.category_names.index(row[self.name])
                    y = condition.category_names.index(row[condition.name])
                    if significance == 'prob':
                        ax.plot([x + min_add, x + min_add],
                                [y + min_add, y + max_add],
                                color, linewidth=line_width)
                        ax.plot([x + max_add, x + max_add],
                                [y + min_add, y + max_add],
                                color, linewidth=line_width)
                    elif significance == 'cond':
                        ax.plot([x + min_add, x + max_add],
                                [y + min_add, y + min_add],
                                color, linewidth=line_width)
                        ax.plot([x + min_add, x + max_add],
                                [y + max_add, y + max_add],
                                color, linewidth=line_width)
                else:
                    y = self.category_names.index(row[self.name])
                    x = condition.category_names.index(row[condition.name])
                    if significance == 'prob':
                        ax.plot([x + min_add, x + max_add],
                                [y + min_add, y + min_add],
                                color, linewidth=line_width)
                        ax.plot([x + min_add, x + max_add],
                                [y + max_add, y + max_add],
                                color, linewidth=line_width)
                    elif significance == 'cond':
                        ax.plot([x + min_add, x + min_add],
                                [y + min_add, y + max_add],
                                color, linewidth=line_width)
                        ax.plot([x + max_add, x + max_add],
                                [y + min_add, y + max_add],
                                color, linewidth=line_width)
        return ax

    def plot_jct(self, other: 'SingleCategoryPTMixin',
                 significance: bool = False,
                 sig_colors: Tuple[str, str] = ('#00ff00', '#ff0000'),
                 sig_values: Tuple[float, float] = (0.945, 0.055),
                 **kwargs) -> Axes:
        """
        Plot a joint count table of self and other.

        :param other: Another SingleCategory to plot against.
        :param significance: Whether to add significance markers to the plot.
                             Equal to p(X=x1,Y=y1) > p(X≠x1, Y≠y1).
        :param sig_colors: Tuple of (high, low) colors for highlighting
                           significance.
        :param sig_values: Tuple of (high, low) values for assessing
                           significance.
        :param kwargs: See utils.plots.plot_pt
        """
        if self.name == other.name:
            raise ValueError('categoricals must have different names')
        if isinstance(other, SingleCategoryPTMixin):
            other_data = other.data
        else:
            # assume multi category
            other_data = other.make_features(naming='{{choice}}')
        # calculate jpt
        jct = create_jct(
            data_1=self.data, data_2=other_data,
            count_1_name=self.name, count_2_name=other.name,
            count_1_order=self.category_names,
            count_2_order=other.category_names
        )
        if 'transpose' not in kwargs.keys():
            kwargs['transpose'] = False
        if 'var_sep' not in kwargs.keys():
            kwargs['var_sep'] = '&'
        if 'dividers' not in kwargs.keys():
            kwargs['dividers'] = False
        kwargs['as_percent'] = False
        kwargs['precision'] = 0
        if 'p_max' not in kwargs.keys():
            kwargs['p_max'] = None
        ax = plot_pt(pt=jct, **kwargs)

        # draw significance values
        if significance and isinstance(other, SingleCategoryPTMixin):
            self._draw_significance_values(
                other=other,
                sig_colors=sig_colors,
                sig_values=sig_values,
                transpose=kwargs['transpose'],
                ax=ax
            )

        return ax
