from matplotlib.axes import Axes
from pandas import Series
from typing import TYPE_CHECKING, Optional

from survey.mixins.filtering import FilterableMixin

if TYPE_CHECKING:
    from survey import Survey


class RespondentAttribute(FilterableMixin, object):
    """
    Represents an Attribute that is present for all Respondents of a Survey.
    """
    name: str
    survey: 'Survey'
    data: Series

    def plot_distribution(
            self, transpose: bool = None,
            data: Optional[Series] = None,
            ax: Optional[Axes] = None, **kwargs
    ):
        raise NotImplementedError

    def where(self, **kwargs) -> 'RespondentAttribute':
        """
        Return a copy of the attribute with only the data where the survey
        matches the given arguments.
        e.g. to filter down to Males who answered 'Yes' to 'q1', use
        question.where(gender='Male', q1='Yes')

        See FilterableMixin.where() for further documentation.
        """
        return super().where(**kwargs)

    def drop_na(self) -> 'RespondentAttribute':

        return super().drop_na()
