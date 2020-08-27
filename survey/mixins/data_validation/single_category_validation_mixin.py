from pandas import Series
from typing import List


class SingleCategoryValidationMixin(object):

    category_names: List[str]

    def _validate_data(self, data: Series):

        errors = []
        for unique_val in data.dropna().unique():
            if unique_val not in self.category_names:
                errors.append(f'"{unique_val}" is not in categories.')
        if errors:
            raise ValueError('\n'.join(errors))
