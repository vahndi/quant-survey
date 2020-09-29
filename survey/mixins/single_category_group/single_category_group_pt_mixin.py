from matplotlib.axes import Axes
from typing import Optional, List

from survey.utils.plots import plot_pt
from survey.utils.probability.prob_utils import create_cpt, create_jpt


class SingleCategoryGroupPTMixin(object):

    name: str
    category_names: List[str]
    items: list

    @property
    def item_dict(self) -> dict:
        raise NotImplementedError

    def cpt(self, item_name: str = 'item', value_name: str = 'value',
            item_names: Optional[List[str]] = None):
        """
        Create a conditional probability table of the answer values for each
        question given the key to the question.

        :param item_name: Name for the collection of questions or attributes to
                          condition on.
        :param value_name: Name for the collection of values to calculate
                           conditional probability of.
        :param item_names: Optional list of names for the questions or
                           attributes instead of the keys.
        """
        if item_names is not None:
            # stack with item names in index
            number_mappings = {item_names.index(name):
                                   name for name in item_names}
            item = self.stack(item_name, number_index=item_name,
                              number_mappings=number_mappings)
            cond_order = item_names
        else:
            # stack with keys in index
            item = self.stack(item_name, key_index=item_name)
            cond_order = [k for q in self.items
                          for k in self.item_dict.keys()
                          if self.item_dict[k] == q]
        instances = item.sentiments.rename(value_name).reset_index()
        index_name = [c for c in instances.columns
                      if c not in (item_name, value_name)][0]
        instances = instances.set_index(index_name)
        cpt = create_cpt(
            prob_data=instances[value_name], cond_data=instances[item_name],
            prob_name=value_name, cond_name=item_name,
            prob_order=self.category_names, cond_order=cond_order
        )
        return cpt

    def jpt(self, item_name: str = 'item', value_name: str = 'value',
            item_names: Optional[List[str]] = None):
        """
        Create a joint probability table of the values for each item with the
        key to the item.

        :param item_name: Name for the collection of questions or attributes to
                          calculate probability of.
        :param value_name: Name for the collection of values to calculate
                           probability of.
        :param item_names: Optional list of names for the questions or
                           attributes instead of the keys.
        """
        if item_names is not None:
            # stack with item names in index
            number_mappings = {item_names.index(name):
                                   name for name in item_names}
            item = self.stack(item_name, number_index=item_name,
                              number_mappings=number_mappings)
            question_order = item_names
        else:
            # stack with keys in index
            item = self.stack(item_name, key_index=item_name)
            question_order = [k for q in self.items
                              for k in self.item_dict.keys()
                              if self.item_dict[k] == q]
        instances = item.sentiments.rename(value_name).reset_index()
        index_name = [c for c in instances.columns
                      if c not in (item_name, value_name)][0]
        instances = instances.set_index(index_name)
        jpt = create_jpt(
            data_1=instances[value_name], data_2=instances[item_name],
            prob_1_name=value_name, prob_2_name=item_name,
            prob_1_order=self.category_names, prob_2_order=question_order
        )
        return jpt

    def plot_cpt(self, item_name: str = 'item', value_name: str = 'value',
                 item_names: Optional[List[str]] = None,
                 **kwargs) -> Axes:
        """
        Plot a conditional probability table of the answer values for each
        question given the key to the question.

        :param item_name: Name for the collection of questions or attributes to
                          condition on.
        :param value_name: Name for the collection of values to calculate
                           conditional probability of.
        :param item_names: Optional list of names for the questions or
                           attributes instead of the keys.
        :param kwargs: See utils.plots.plot_pt
        """
        cpt = self.cpt(item_name=item_name, value_name=value_name,
                       item_names=item_names)
        if 'transpose' not in kwargs.keys():
            kwargs['transpose'] = True
        if 'var_sep' not in kwargs:
            kwargs['var_sep'] = '|'
        ax = plot_pt(pt=cpt, **kwargs)
        return ax

    def plot_jpt(self, item_name: str = 'item', value_name: str = 'value',
                 item_names: Optional[List[str]] = None,
                 **kwargs) -> Axes:
        """
        Plot a joint probability table of the answer values for each question
        with the key to the question.

        :param item_name: Name for the collection of questions or attributes to
        condition on.
        :param value_name: Name for the collection of values to calculate
                           conditional probability of.
        :param item_names: Optional list of names for the questions or
                           attributes instead of the keys.
        :param kwargs: See utils.plots.plot_pt
        """
        jpt = self.jpt(item_name=item_name, value_name=value_name,
                       item_names=item_names)
        if 'transpose' not in kwargs.keys():
            kwargs['transpose'] = True
        if 'var_sep' not in kwargs:
            kwargs['var_sep'] = ','
        if 'dividers' not in kwargs:
            kwargs['dividers'] = False
        ax = plot_pt(pt=jpt, **kwargs)
        return ax
