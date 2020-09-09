from matplotlib.axes import Axes, SubplotBase
from matplotlib.axis import Axis
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from mpl_format.axes.axis_utils import new_axes
from mpl_format.text.text_utils import wrap_text, map_text
from numpy.ma import arange
from pandas import concat, DataFrame, Series, value_counts
from pathlib import Path
from seaborn import heatmap, distplot, kdeplot, JointGrid, PairGrid
from typing import Callable, List, Union, Optional, TypeVar, Dict, Tuple

from survey.utils.data_frames import sort_data_frame_values

PlotObject = TypeVar('PlotObject', Axes, Figure, JointGrid, PairGrid)


def save_figure(plot_object: PlotObject,
                file_path: Union[str, Path],
                file_type: str = 'png'):
    """
    Save a plot object to disk.

    :param plot_object: The plot object to save to disk,
    :param file_path: The file path to save the plot object to.
    :param file_type: The type of file to save
    """
    if isinstance(file_path, Path):
        file_path = str(file_path)
    kwargs = {}
    plot_obj_type = type(plot_object)
    if (
            plot_obj_type is Axes or
            issubclass(plot_obj_type, Axes) or
            issubclass(plot_obj_type, SubplotBase)
    ):
        fig = plot_object.figure
        kwargs['dpi'] = fig.dpi
    elif plot_obj_type is Figure:
        fig = plot_object
        kwargs['dpi'] = fig.dpi
    elif plot_obj_type in (JointGrid, PairGrid):
        fig = plot_object
    else:
        raise ValueError(
            f'plot_object must be one of Axes, Figure, JointGrid, PairGrid. '
            f'Type passed was {plot_object}'
        )
    fig.savefig(
        '%s%s' % (
            file_path,
            ('.' + file_type if not file_path.endswith('.' + file_type) else '')
        ),
        **kwargs
    )


def draw_horizontal_dividers(ax: Axes, color: str = 'k') -> Axes:
    """
    Draw horizontal dividers onto a heatmap.

    :param ax: Axes to draw onto
    :param color: Color of the lines to draw
    """
    x_lim = [int(x) for x in ax.get_xlim()]
    y_lim = [int(y) for y in ax.get_ylim()]
    y_div = range(min(y_lim), max(y_lim) + 1)
    ax.hlines(y=y_div, xmin=min(x_lim), xmax=max(x_lim), colors=color)
    ax.vlines(x=[min(x_lim), max(x_lim)], ymin=min(y_lim), ymax=max(y_lim))
    return ax


def draw_vertical_dividers(ax: Axes, color: str = 'k') -> Axes:
    """
    Draw vertical dividers onto a heatmap.

    :param ax: Axes to draw onto
    :param color: Color of the lines to draw
    """
    x_lim = [int(x) for x in ax.get_xlim()]
    y_lim = [int(y) for y in ax.get_ylim()]
    x_div = range(min(x_lim), max(x_lim) + 1)
    ax.vlines(x=x_div, ymin=min(y_lim), ymax=max(y_lim) + 1, colors=color)
    ax.hlines(y=[min(y_lim), max(y_lim)], xmin=min(x_lim), xmax=max(x_lim))
    return ax


def set_cpt_axes_labels(ax: Axes,
                        x_label: Union[bool, str], y_label: Union[bool, str],
                        cond_name: str, prob_name: str, transpose: bool):
    """
    Set axes labels for a conditional probability table plot.

    :param ax: The axes whose labels to set.
    :param x_label: String for the x-axis label; True to label with probability,
                    or False to use no label.
    :param y_label: String for the y-axis label; True to label with condition,
                    or False to use no label.
    :param cond_name: Name of the conditional variable.
    :param prob_name: Name of the probability variable.
    :param transpose: Whether the plot is transposed. If `x_label` and `y_label`
                      are `True`, used to flip the axis labeling.
    """
    cond_label = wrap_text(cond_name)
    prob_label = wrap_text(prob_name)
    label_x = (
        x_label if type(x_label) is str else
        (cond_label if transpose else prob_label) if x_label
        else ''
    )
    label_y = (
        y_label if type(y_label) is str else
        (prob_label if transpose else cond_label) if y_label
        else ''
    )
    ax.set_xlabel(label_x)
    set_axis_tick_label_rotation(ax.xaxis, 90)
    ax.set_ylabel(label_y)
    set_axis_tick_label_rotation(ax.yaxis, 0)


def set_jpd_axes_labels(ax: Axes,
                        x_label: Union[bool, str], y_label: Union[bool, str],
                        prob_1_name: str, prob_2_name: str,
                        transpose: bool):
    """
    Set axes labels for a joint probability distribution plot.

    :param ax: The axes whose labels to set.
    :param x_label: String for the x-axis label; True to label with probability,
                    or False to use no label.
    :param y_label: String for the y-axis label; True to label with condition,
                    or False to use no label.
    :param prob_1_name: Name of the first probability variable.
    :param prob_2_name: Name of the second probability variable.
    :param transpose: Whether the plot is transposed. If `x_label` and `y_label`
                      are `True`, used to flip the axis labeling.
    """
    prob_1_label = wrap_text(prob_1_name)
    prob_2_label = wrap_text(prob_2_name)
    label_x = (
        x_label if type(x_label) is str else
        (prob_2_label if transpose else prob_1_label) if x_label
        else ''
    )
    label_y = (
        y_label if type(y_label) is str else
        (prob_1_label if transpose else prob_2_label) if y_label
        else ''
    )
    ax.set_xlabel(label_x)
    set_axis_tick_label_rotation(ax.xaxis, 90)
    ax.set_ylabel(label_y)
    set_axis_tick_label_rotation(ax.yaxis, 0)


def set_cpd_axes_labels(ax: Axes, x_label: bool, y_label: bool,
                        prob_name: str, transpose: bool):
    """
    Set axes labels for a conditional probability distribution plot.

    :param ax: The axes whose labels to set.
    :param x_label: String for the x-axis label; True to label with probability,
                    or False to use no label.
    :param y_label: String for the y-axis label; True to label with condition,
                    or False to use no label.
    :param prob_name: Name of the probability variable.
    :param transpose: Whether the plot is transposed. If `x_label` and `y_label`
                      are `True`, used to flip the axis labeling.
    """
    label_x = 'p(respondent)' if transpose else wrap_text(prob_name)
    label_y = wrap_text(prob_name) if transpose else 'p(respondent)'
    if x_label:
        ax.set_xlabel(label_x)
    else:
        ax.set_xlabel('')
    if y_label:
        ax.set_ylabel(label_y)
        set_axis_tick_label_rotation(ax.yaxis, 0)
    else:
        ax.set_ylabel('')


def set_cp_tick_labels(ax: Axes, x_tick_labels: bool, y_tick_labels: bool):
    """
    Turn of tick labels if False is passed.

    :param ax: Axes with tick labels.
    :param x_tick_labels: Whether to use tick labels for the x-axis.
    :param y_tick_labels: Whether to use tick labels for the y-axis.
    :return:
    """
    if not x_tick_labels:
        ax.set_xticklabels([])
    if not y_tick_labels:
        ax.set_yticklabels([])


def set_axis_tick_label_rotation(ax: Axis, rotation: int):
    """
    Set the rotation of axis tick labels.

    :param ax: The axis whose tick label rotation to set.
    :param rotation: The rotation value to set.
    """
    if ax.get_majorticklabels():
        plt.setp(ax.get_majorticklabels(), rotation=rotation)
    if ax.get_minorticklabels():
        plt.setp(ax.get_minorticklabels(), rotation=rotation)


def plot_categorical_distribution(
        categorical_data: Series, title: str = '',
        order: list = None,
        transpose: bool = False,
        x_label: bool = True, y_label: bool = True,
        x_tick_labels: bool = True, y_tick_labels: bool = True,
        color: Union[str, List[str]] = 'C0',
        edge_color: Union[Optional[str], Optional[List[str]]] = None,
        line_style: Optional[str] = None,
        line_width: Union[Optional[str], Optional[List[str]]] = None,
        ax: Optional[Axes] = None, pct_size: Optional[int] = None,
        label_mappings: Optional[Dict[str, str]] = None,
        drop_na: bool = True,
        max_axis_label_chars: int = None,
        grid: bool = False,
        y_lim: Optional[Tuple[int, int]] = None,
        alpha: float = 1.0
) -> Axes:
    """
    Create a bar-plot of the counts of a categorical variable.

    :param categorical_data: The data to plot e.g. a sequence of answers
                             or attribute values.
    :param title: The title for the plot.
    :param order: Optional list of labels to order the plotted categories by.
    :param transpose: True to plot horizontal bars.
    :param x_label: Whether to add a label to the x-axis.
    :param y_label: Whether to add a label to the y-axis.
    :param x_tick_labels: Whether to show labels on the ticks on the x-axis.
    :param y_tick_labels: Whether to show labels on the ticks on the y-axis.
    :param color: Single color or list of colors for bars.
    :param edge_color: Single color or list of colors for bar edges.
    :param line_style: Line style for bar edges.
    :param line_width: Single width or list of widths for bar edges.
    :param pct_size: Font size for percentage labels.
    :param ax: Optional matplotlib axes to plot on.
    :param label_mappings: Optional mappings to modify axis labels.
    :param drop_na: Whether to exclude null values from the percentage counts.
    :param max_axis_label_chars: Maximum number of characters before wrapping
                                 axis labels.
    :param grid: Whether to show a grid.
    :param y_lim: Optional limits for the y-axis.
    """
    plot_type = 'barh' if transpose else 'bar'
    item_counts = categorical_data.value_counts()
    if order:
        # add zero value for missing categories
        for item_name in order:
            if item_name not in item_counts.index:
                item_counts = item_counts.append(Series({item_name: 0}))
        # sort categories for plot
        item_counts = item_counts.reindex(order)
    ax = ax or new_axes()
    if label_mappings is not None:
        item_counts.index = wrap_text(
            map_text(item_counts.index, label_mappings),
            max_axis_label_chars
        )
    else:
        item_counts.index = wrap_text(item_counts.index, max_axis_label_chars)
    item_counts.plot(kind=plot_type, ax=ax, color=color, edgecolor=edge_color,
                     linestyle=line_style, linewidth=line_width, alpha=alpha)
    # add percentages
    item_pcts = 100 * item_counts.div(
        len(categorical_data) if not drop_na
        else len(categorical_data.dropna())
    )
    label_bar_plot_pcts(item_counts=item_counts, item_pcts=item_pcts,
                        ax=ax, transpose=transpose, font_size=pct_size)
    # add titles
    ax.set_title(title)
    if transpose:
        x_label_value = '# Respondents'
        y_label_value = categorical_data.name
    else:
        x_label_value = categorical_data.name
        y_label_value = '# Respondents'
    if x_label:
        ax.set_xlabel(x_label_value)
    else:
        ax.set_xlabel('')
    if y_label:
        ax.set_ylabel(y_label_value)
    else:
        ax.set_ylabel('')
    if not x_tick_labels:
        ax.set_xticklabels([])
    if not y_tick_labels:
        ax.set_yticklabels([])
    if grid:
        ax.grid(True)
        ax.set_axisbelow(True)
    if y_lim is not None:
        ax.set_ylim(y_lim)

    return ax


def label_bar_plot_pcts(item_counts: Series, item_pcts: Series, ax: Axes,
                        transpose: bool, font_size: Optional[int] = None):
    """
    Label a bar plot with percentage labels.

    :param item_counts: Count of each item in the plot.
    :param item_pcts: Percentage of each item in the plot.
    :param ax: Matplotlib axes containing the bars to label.
    :param transpose: Whether the plot is transposed (barh).
    :param font_size: Size of the font for the percentage labels.
    """
    for item, count in item_counts.items():
        if transpose:
            text_x = count
            text_y = item_counts.index.get_loc(item)
            ha, va = 'left', 'center'
        else:
            text_x = item_counts.index.get_loc(item)
            text_y = count
            ha, va = 'center', 'bottom'
        ax.text(
            x=text_x, y=text_y,
            s=f'{item_pcts.loc[item]:0.1f}%',
            ha=ha, va=va,
            fontsize=font_size
        )


def plot_categorical_distributions(data: List[Series], order: List[str] = None,
                                   sort_by: Union[str, Callable, list] = None,
                                   ax: Optional[Axes] = None) -> Axes:
    """
    Plot a comparison of several categorical distributions
    e.g. a list of LikertQuestion responses.

    :param data: List of response data to Categorical Questions
    :param order: Optional ordering for the Categorical values
    :param sort_by: Column name(s) and/or lambda function(s) to sort by
                    e.g. lambda d: d['1'] + d['2']
    :param ax: Optional matplotlib axes to plot on.
    """
    joined = concat(data, axis=1)
    counts = joined.apply(value_counts).fillna(0).T
    if order:
        counts = counts[order]
        if sort_by is None:
            sort_by = order
        counts = sort_data_frame_values(counts, sort_by, ascending=False)
    counts.index = wrap_text(counts.index)
    ax = ax or new_axes()
    counts.plot(kind='bar', stacked=True, ax=ax)
    percentages = counts.astype(float)
    percentages = 100 * (percentages.T / percentages.T.sum()).T
    for label_x in range(percentages.shape[0]):
        y_base = 0
        for count_y in range(percentages.shape[1]):
            y = y_base + counts.iloc[label_x, count_y] / 2
            text = f'{percentages.iloc[label_x, count_y]:.1f}%'
            ax.text(x=label_x, y=y, s=text, ha='center', va='center')
            y_base += counts.iloc[label_x, count_y]
    return ax


def plot_pt(pt: DataFrame, transpose: bool = True,
            set_title: bool = True, cbar: bool = True,
            x_label: Union[bool, str] = True,
            y_label: Union[bool, str] = True,
            x_tick_labels: bool = True, y_tick_labels: bool = True,
            dividers: bool = True,
            as_percent: bool = True, precision: int = None,
            p_max: float = 1.0, var_sep: str = '|', ax: Optional[Axes] = None,
            pct_size: int = None, cmap: str = 'Blues',
            min_pct: Optional[int] = None,
            label_mappings: Optional[Dict[str, str]] = None,
            max_axis_label_chars: int = None) -> Axes:
    """
    Plot a probability table.

    :param pt: DataFrame with condition as index and probability as
               columns (for cpts) or 2 probs (for jpts).
    :param transpose: Set to True to put `condition` on x-axis.
    :param cbar: Whether to show the color-bar.
    :param set_title: Whether to add a title to the plot.
    :param x_label: Whether to show the default label on the x-axis or not,
                    or string of text for the label.
    :param y_label: Whether to show the default label on the y-axis or not,
                    or string of text for the label.
    :param x_tick_labels: Whether to show labels on the ticks on the x-axis.
    :param y_tick_labels: Whether to show labels on the ticks on the y-axis.
    :param dividers: Whether to show dividing lines between each condition.
    :param as_percent: Whether to show probabilities as a percentage.
    :param precision: Number of decimal places to display values.
                      Defaults to 1 for proportions, 2 for percentages.
    :param p_max: The value for the highest probability (0 to 1).
    :param var_sep: The separator to use between variables in the title
                    e.g. '|' for conditional, ',' for joint
    :param ax: Optional matplotlib axes to plot on.
    :param cmap: Name of the colormap.
    :param pct_size: Size of the font for the percent labels.
    :param min_pct: Minimum sum of percentages across rows / columns
                    to keep those rows / columns.
    :param label_mappings: Optional dict of replacements for labels.
    """
    # calculate cpt and fix labels
    p1 = pt.index.name
    p2 = pt.columns.name
    if transpose:
        pt = pt.T
    pt.index = wrap_text(map_text(pt.index, label_mappings),
                         max_axis_label_chars)
    pt.columns = wrap_text(map_text(pt.columns, label_mappings),
                           max_axis_label_chars)
    if as_percent:
        precision = precision if precision is not None else 1
        fmt = f'.{precision}%'
        v_max = p_max
        cbar_kws = {'format': FuncFormatter(lambda x, pos: f'{x:.0%}')}
    else:
        precision = precision if precision is not None else 2
        fmt = f'.{precision}f'
        v_max = p_max if p_max is not None else None
        cbar_kws = {}
    ax = ax or new_axes()
    # plot
    if min_pct is not None:
        pt = pt.reindex(index=pt.loc[(pt.sum(axis=1) > min_pct)].index,
                        columns=pt.loc[:, pt.sum(axis=0) > min_pct].columns)
    heatmap(pt, annot=True, cbar=cbar,
            vmin=0, vmax=v_max, fmt=fmt, cmap=cmap,
            linewidths=1, linecolor='#bbbbbb', cbar_kws=cbar_kws,
            annot_kws={'fontsize': pct_size} if pct_size is not None else {},
            ax=ax)
    ax.invert_yaxis()
    if dividers:
        if transpose:
            draw_vertical_dividers(ax)
        else:
            draw_horizontal_dividers(ax)
    # set labels
    set_cpt_axes_labels(ax=ax, x_label=x_label, y_label=y_label,
                        cond_name=p1, prob_name=p2,
                        transpose=transpose)
    set_cp_tick_labels(ax, x_tick_labels, y_tick_labels)
    if set_title:
        if as_percent:
            ax.set_title(f'p({p2}{var_sep}{p1})')
        else:
            ax.set_title(f'|{p2}{var_sep}{p1}|')

    return ax


def plot_cpd(survey_data: DataFrame, probability: str, condition: str,
             transpose: bool = False,
             set_title: bool = True, legend: bool = True,
             x_label: bool = True, y_label: bool = True,
             x_tick_labels: bool = True, y_tick_labels: bool = True,
             ax: Optional[Axes] = None) -> Axes:
    """
    Plot a conditional probability distribution as a kde for each condition
    category.

    :param survey_data: The DataFrame containing the survey data.
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
    condition_data = survey_data[condition]
    prob_data = survey_data[probability].dropna()
    ax = ax or new_axes()
    for category in condition_data.unique():
        distplot(
            a=prob_data.loc[condition_data == category],
            kde=True, rug=True, hist=False,
            ax=ax, label=category, vertical=transpose
        )
    ax.legend(title=condition).set_visible(legend)
    # label axes
    set_cpd_axes_labels(ax=ax, x_label=x_label, y_label=y_label,
                        prob_name=probability, transpose=transpose)
    set_cp_tick_labels(ax, x_tick_labels, y_tick_labels)
    # axes limits
    if transpose:
        if prob_data.min() <= prob_data.max() / 10:
            ax.set_ylim(0, ax.get_ylim()[1])
    else:
        if prob_data.min() <= prob_data.max() / 10:
            ax.set_xlim(0, ax.get_xlim()[1])
    # title
    if set_title:
        ax.set_title(f'p({probability}|{condition})')
    return ax


def plot_jpd(survey_data: DataFrame, prob_1: str, prob_2: str,
             kind: str = 'kde',
             transpose: bool = False, set_title: bool = True,
             legend: bool = False,
             x_label: bool = True, y_label: bool = True,
             x_tick_labels: bool = True, y_tick_labels: bool = True,
             ax: Optional[Axes] = None) -> Axes:
    """
    Plot a joint probability distribution of 2 columns. 
    
    :param survey_data: The DataFrame containing the survey data.
    :param prob_1: The first marginal probability distribution.
    :param prob_2: The second marginal probability distribution.
    :param kind: 'kde' or 'scatter'
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
    if kind not in ('kde', 'scatter', 'hist2d'):
        raise ValueError('Only kde, scatter and hist2d plots'
                         ' are currently supported')
    # get data
    survey_data = survey_data.dropna(subset=[prob_1, prob_2])
    if kind == 'kde':
        survey_data = survey_data.loc[
            (survey_data[prob_1] > survey_data[prob_1].max() / 100) &
            (survey_data[prob_2] > survey_data[prob_2].max() / 100)
        ]  # very small relative values sometimes lead to an empty plot
    if transpose:
        x_data = survey_data[prob_2]
        y_data = survey_data[prob_1]
    else:
        x_data = survey_data[prob_1]
        y_data = survey_data[prob_2]
    # plot
    ax = ax or new_axes()
    if kind == 'kde':
        kdeplot(
            data=x_data, data2=y_data,
            shade=True, cmap='Blues', ax=ax
        )
    elif kind == 'scatter':
        ax.scatter(x=x_data, y=y_data, color='g', alpha=0.1)
    elif kind == 'hist2d':
        if (x_data.astype(int) - x_data).sum() == 0:
            x_bins = arange(x_data.min() - 0.5, x_data.max() + 1.5)
        else:
            x_bins = 100
        if (y_data.astype(int) - y_data).sum() == 0:
            y_bins = arange(y_data.min() - 0.5, y_data.max() + 1.5)
        else:
            y_bins = 100
        ax.hist2d(x=x_data, y=y_data, cmap='Blues', bins=(x_bins, y_bins))
    # label axes
    set_jpd_axes_labels(ax=ax, x_label=x_label, y_label=y_label,
                        prob_1_name=prob_1, prob_2_name=prob_2,
                        transpose=transpose)
    set_cp_tick_labels(ax, x_tick_labels, y_tick_labels)
    #  set axis ranges
    if 0 <= x_data.min() < x_data.max() / 10:
        ax.set_xlim(0, ax.get_xlim()[1])
    if 0 <= y_data.min() < y_data.max() / 10:
        ax.set_ylim(0, ax.get_ylim()[1])
    if legend:
        ax.legend()
    # title
    if set_title:
        ax.set_title(f'p({prob_1}, {prob_2})')
    return ax


def label_pair_bar_plot_pcts(
        item_counts: DataFrame, item_pcts: DataFrame,
        ax: Axes, transpose: bool, font_size: Optional[int] = None
):

    for r, response in enumerate(item_counts.index):
        for q, question in enumerate(item_counts.columns):
            count = item_counts.loc[response, question]
            pct = item_pcts.loc[response, question]
            if transpose:
                text_x = count
                text_y = r + 0.125 + 0.25 * (q - 1)
                ha, va = 'left', 'center'
            else:
                text_x = r + 0.125 + 0.25 * (q - 1)
                text_y = count
                ha, va = 'center', 'bottom'
            ax.text(
                x=text_x, y=text_y,
                s=f'{pct:0.1f}%',
                ha=ha, va=va,
                fontsize=font_size
            )
