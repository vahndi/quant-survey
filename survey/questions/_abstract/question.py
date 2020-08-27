from matplotlib.axes import Axes
from numpy import nan
from pandas import Series, notnull
from typing import TYPE_CHECKING, Optional

from survey.mixins.filtering import FilterableMixin

if TYPE_CHECKING:
    from survey import Survey


class Question(FilterableMixin, object):
    """
    Class to represent a Survey Question.
    """
    name: str
    text: str
    survey: 'Survey'
    data: Series

    def plot_distribution(
            self,
            transpose: bool = None,
            data: Optional[Series] = None,
            ax: Optional[Axes] = None,
            **kwargs
    ):

        raise NotImplementedError

    def where(self, **kwargs) -> 'Question':
        """
        Return a copy of the question with only the data where the survey
        matches the given arguments e.g. to filter down to Males who answered
        'Yes' to 'q1', use question.where(gender='Male', q1='Yes').

        See FilterableMixin.where() for further documentation.
        """
        return super().where(**kwargs)

    def drop_na(self) -> 'Question':

        return super().drop_na()

    def _get_merge_data(self, other: 'Question') -> Series:

        if set(
            self.data.dropna().index
        ).intersection(other.data.dropna().index):
            raise ValueError("Can't merge questions which both "
                             "have values for a given index location.")
        if set(self.data.index) != set(other.data.index):
            raise ValueError('Can only merge question with the same index.')
        new_data = Series(
            data=(
                self.data[ix] if notnull(self.data[ix]) else
                other.data[ix] if notnull(other.data[ix]) else
                nan for ix in self.data.index
            ), index=self.data.index
        )
        return new_data

    def _update_init_dict(self, init_dict: dict, *args) -> dict:

        for arg in args:
            if arg not in init_dict.keys():
                init_dict[arg] = getattr(self, arg)
        return init_dict
