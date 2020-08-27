from pandas import Series


class PositiveMeasureValidationMixin(object):

    def _validate_data(self, data: Series):

        data = data.dropna()
        if (data < 0).sum() != 0:
            raise ValueError('Data for PositiveMeasure must be non-negative.')
