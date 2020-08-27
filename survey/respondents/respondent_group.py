class RespondentGroup(object):

    def __init__(self, respondent_values: dict, response_values: dict):

        self._respondent_values = respondent_values
        self._response_values = response_values

    @property
    def respondent_values(self):

        return self._respondent_values

    @property
    def response_values(self):

        return self._response_values

    def __eq__(self, other: 'RespondentGroup') -> bool:

        return (
            self._response_values == other._response_values and
            self._respondent_values == other._respondent_values
        )

    def __repr__(self):

        return (
            f'RespondentGroup('
            f'\n\tattribute_values={self._respondent_values},'
            f'\n\tresponse_values={self._response_values}'
            f'\n)'
        )
