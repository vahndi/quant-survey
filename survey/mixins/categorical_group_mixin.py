import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import List, Union, Dict, Optional, Tuple, Any

from survey.mixins.data_types.categorical_mixin import CategoricalMixin


class CategoricalGroupMixin(object):

    items: List[CategoricalMixin]

    def _set_categories(self):
        """
        Set the Categories for the Group if all Categoricals in the Group have
        the same Categories.
        """
        ref_names = set(self.items[0].category_names)
        all_names = set([
            category_name for item in self.items
            for category_name in item.category_names
        ])
        if ref_names == all_names:
            self._categories = self.items[0].categories
        else:
            self._categories = None

    @property
    def categories(self) -> Optional[Union[List[str], Dict[str, int]]]:
        """
        Return the categories.
        """
        return self._categories

    @property
    def category_names(self) -> Optional[List[str]]:
        """
        Return the names of the categories.
        """
        if isinstance(self._categories, list):
            return self._categories
        elif isinstance(self._categories, dict):
            return list(self._categories.keys())
        else:
            return None

    @property
    def category_values(self) -> Optional[list]:
        """
        Return the values of the categories.
        """
        if isinstance(self._categories, list):
            return self._categories
        elif isinstance(self._categories, dict):
            return list(self._categories.values())
        else:
            return None

    def plot_distribution_grid(
            self, n_rows: int, n_cols: int,
            fig_size: Optional[Tuple[int, int]] = (16, 9),
            filters: Optional[Dict[str, Any]] = None,
            titles: Union[str, List[str], Dict[str, str]] = '',
            x_labels: Union[str, List[str], Dict[str, str]] = '',
            drop: Optional[Union[str, List[str]]] = None,
            **kwargs
    ) -> Figure:
        """
        Plot a grid of distributions of the group's questions.

        :param n_rows: Number of rows in the grid.
        :param n_cols: Number of columns in the grid.
        :param fig_size: Size for the figure.
        :param filters: Optional filters to apply to each question before
                        plotting.
        :param titles: List of titles or dict mapping question keys or names to
                       titles.
        :param x_labels: List of x-axis labels or dict mapping question keys or
                         names to labels.
        :param drop: Optional category or categories to exclude from the plot.
        :param kwargs: Other kwargs to pass to each question's
                       plot_distribution() method.
        """
        categories = set(self._questions[0].categories)
        share_x = 'all'
        for item in self.items[1:]:
            if set(item.categories) != categories:
                share_x = 'none'
        fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols,
                                 figsize=fig_size,
                                 sharex=share_x, sharey='all')

        for i, item in enumerate(self.items):
            ax = axes.flat[i]
            if filters is not None:
                item = item.where(**filters)
            if drop is not None:
                item = item.drop(drop)
            item.plot_distribution(ax=ax, **kwargs)
            if isinstance(titles, str):
                ax.set_title(titles)
            elif isinstance(titles, list):
                ax.set_title(titles[i])
            elif isinstance(titles, dict):
                if item.name in titles.keys():
                    ax.set_title(titles[item.name])
                elif self.find_key(item) in titles.keys():
                    ax.set_title(titles[self.find_key(item)])
            if isinstance(x_labels, str):
                ax.set_xlabel(x_labels)
            elif isinstance(x_labels, list):
                ax.set_xlabel(x_labels[i])
            elif isinstance(x_labels, dict):
                if item.name in x_labels.keys():
                    ax.set_xlabel(x_labels[item.name])
                elif self.find_key(item) in titles.keys():
                    ax.set_xlabel(x_labels[self.find_key(item)])

        return fig

    def plot_comparison_grid(
            self,
            other: 'CategoricalGroupMixin',
            n_rows: int, n_cols: int,
            filters: Optional[Dict[str, Any]] = None,
            self_color: str = 'C0', other_color: str = 'C1',
            self_name: Optional[str] = None, other_name: Optional[str] = None,
            fig_size: Optional[Tuple[int, int]] = (16, 9),
            titles: Union[str, List[str], Dict[str, str]] = '',
            x_labels: Union[str, List[str], Dict[str, str]] = '',
            **kwargs) -> Figure:
        """
        Plot a grid of distributions of comparisons between the corresponding
        questions of 2 groups.

        :param other: The other group to use.
        :param n_rows: Number of rows in the grid.
        :param n_cols: Number of columns in the grid.
        :param self_color: Color for this group's plot items.
        :param other_color: Color for the other group's plot items.
        :param self_name: Name for this group's plot items.
        :param other_name: Name for the other group's plot items.
        :param fig_size: Size for the figure.
        :param filters: Optional filters to apply to each question before
                        plotting.
        :param titles: List of titles or dict mapping question keys or names to
                       titles.
        :param x_labels: List of x-axis labels or dict mapping question keys or
                         names to labels.
        :param kwargs: Other kwargs to pass to each question's
                       plot_distribution() method.
        """
        categories = set(self._questions[0].categories)
        share_x = 'all'
        for item in self.items[1:]:
            if set(item.categories) != categories:
                share_x = 'none'
        fig, axes = plt.subplots(
            nrows=n_rows, ncols=n_cols,
            figsize=fig_size,
            sharex=share_x, sharey='all'
        )
        if [self_name, other_name].count(None) not in (0, 2):
            raise ValueError(
                'Either rename both question groups or neither.'
            )
        if self_name is not None and self_name == other_name:
            raise ValueError(
                'Names of questions must be different to plot a comparison.'
            )

        for i, item in enumerate(self.items):
            ax = axes.flat[i]
            if self_name is None and other_name is None:
                if item.name == other.items[i].name:
                    raise ValueError('Names of questions must be different'
                                     ' to plot a comparison.')
            self_item = (
                item.rename(self_name) if self_name is not None else item
            )
            other_item = (
                other.items[i].rename(other_name) if other_name is not None
                else other.items[i]
            )
            if filters is not None:
                self_item = self_item.where(**filters)
                other_item = other_item.where(**filters)
            self_item.plot_comparison(
                other_item,
                ax=ax, self_color=self_color,
                other_color=other_color, **kwargs
            )
            if isinstance(titles, str):
                ax.set_title(titles)
            elif isinstance(titles, list):
                ax.set_title(titles[i])
            elif isinstance(titles, dict):
                if item.name in titles.keys():
                    ax.set_title(titles[item.name])
                elif self.find_key(item) in titles.keys():
                    ax.set_title(titles[self.find_key(item)])
            if isinstance(x_labels, str):
                ax.set_xlabel(x_labels)
            elif isinstance(x_labels, list):
                ax.set_xlabel(x_labels[i])
            elif isinstance(x_labels, dict):
                if item.name in x_labels.keys():
                    ax.set_xlabel(x_labels[item.name])
                elif self.find_key(item) in titles.keys():
                    ax.set_xlabel(x_labels[self.find_key(item)])

        return fig
