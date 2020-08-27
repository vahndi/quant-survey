from pandas import Series


class CountValidationMixin(object):

    def _validate_data(self, data: Series):

        data = data.dropna()
        if (data < 0).sum() != 0:
            raise ValueError(
                'Data for CountQuestion must be non-negative.'
            )
        if (data != data.astype(int)).sum() != 0:
            raise ValueError(
                'Data for CountQuestion should be integers only.'
            )
