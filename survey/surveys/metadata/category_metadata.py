from pandas import DataFrame
from typing import List


class CategoryMetadata(object):

    def __init__(self, name: str, values: list):
        """
        Create metadata for a category.

        :param name: The name of the category.
        :param values: The values of the category.
        """
        self._name = name
        self._values = values

    @staticmethod
    def from_dataframe(data: DataFrame) -> List['CategoryMetadata']:
        """
        Create a list of CategoryMetadata's from a pandas DataFrame

        :param data: DataFrame containing columns with the names of
                     CategoryMetadata attributes.
        """
        category_metas = []
        for name in data['name'].unique():
            values = data.loc[data['name'] == name, 'values'].unique().tolist()
            category_metas.append(CategoryMetadata(
                name=name, values=values
            ))
        return category_metas

    @property
    def name(self) -> str:
        return self._name

    @property
    def values(self) -> List[str]:
        return self._values
