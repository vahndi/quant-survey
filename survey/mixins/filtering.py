from copy import copy
from pandas import Series, notnull
from typing import TYPE_CHECKING

from survey.constants import CATEGORY_SPLITTER

if TYPE_CHECKING:
    from survey.surveys.survey import Survey


class FilterableMixin(object):

    survey: 'Survey'
    data: Series

    def where(self, **kwargs):
        """
        Return a copy of the question with only the data where the survey
        matches the given arguments. e.g. to filter down to Males who
        answered 'Yes' to 'q1', use question.where(gender='Male', q1='Yes')

        To use other filters, append '__filter_type' to the argument e.g.
        gender__ne='Male' for non-males. Valid filters are `ne`, `lt`, `gt`,
        `le`, `ge`, `in`, `not_in`, `contains`, `selected`, `not_selected`,
        `is_null`, `not_null`, or a lambda function that returns True for rows
        that should be included.
        """
        clone = copy(self)
        survey_data = self.survey.data
        index = survey_data.index.tolist()
        for variable, value in kwargs.items():
            if variable.endswith('__ne'):
                search_ix = set(
                    survey_data.loc[survey_data[variable[: -4]] != value].index)
            elif variable.endswith('__lt'):
                search_ix = set(
                    survey_data.loc[survey_data[variable[: -4]] < value].index)
            elif variable.endswith('__gt'):
                search_ix = set(
                    survey_data.loc[survey_data[variable[: -4]] > value].index)
            elif variable.endswith('__le'):
                search_ix = set(
                    survey_data.loc[survey_data[variable[: -4]] <= value].index)
            elif variable.endswith('__ge'):
                search_ix = set(
                    survey_data.loc[survey_data[variable[: -4]] >= value].index)
            elif variable.endswith('__in'):
                search_ix = set(
                    survey_data.loc[
                        survey_data[variable[: -4]
                        ].isin(value)].index)
            elif variable.endswith('__not_in'):
                search_ix = set(
                    survey_data.loc[
                        ~survey_data[variable[: -8]
                        ].isin(value)].index)
            elif variable.endswith('__contains'):
                search_ix = set(
                    survey_data.loc[
                        survey_data[variable[: -10]
                        ].astype(str).str.contains(value)].index)
            elif variable.endswith('__selected'):  # only for MultiChoice
                item_name = variable[: -10]
                data: Series = survey_data[item_name]
                value_set = {value} if isinstance(value, str) else set(value)
                is_match = Series(
                    index=data.index,
                    data=[value_set.issubset(
                              str_selections.split(CATEGORY_SPLITTER)
                          ) if notnull(str_selections)
                          else False for _, str_selections in data.iteritems()]
                )
                search_ix = is_match.loc[is_match == True].index
            elif variable.endswith('__not_selected'):  # only for MultiChoice
                item_name = variable[: -14]
                data: Series = survey_data[item_name]
                value_set = {value} if isinstance(value, str) else set(value)
                is_match = Series(
                    index=data.index,
                    data=[len(value_set.intersection(
                                  str_selections.split(CATEGORY_SPLITTER))
                          ) == 0 if notnull(str_selections)
                          else False for _, str_selections in data.iteritems()]
                )
                search_ix = is_match.loc[is_match == True].index
            elif variable.endswith('__not_null'):
                item_name = variable[: -10]
                if value is True:
                    search_ix = set(
                        survey_data.loc[survey_data[item_name].notnull()].index
                    )
                elif value is False:
                    search_ix = set(
                        survey_data.loc[survey_data[item_name].isnull()].index
                    )
                else:
                    raise ValueError(
                        'Must pass either True or False to not_null filter.'
                    )
            elif variable.endswith('__is_null'):
                item_name = variable[: -9]
                if value is True:
                    search_ix = set(
                        survey_data.loc[survey_data[item_name].isnull()].index
                    )
                elif value is False:
                    search_ix = set(
                        survey_data.loc[survey_data[item_name].notnull()].index
                    )
                else:
                    raise ValueError(
                        'Must pass either True or False to is_null filter.'
                    )
            elif callable(variable):
                search_ix = set(
                    survey_data.loc[survey_data[variable].map(value)].index
                )
            else:
                search_ix = set(
                    survey_data.loc[survey_data[variable] == value].index
                )
            index = [i for i in index if i in search_ix]
        clone.data = self.data.reindex(index)
        return clone

    def drop_na(self):

        clone = copy(self)
        clone.data = self.data.dropna()
        return clone
