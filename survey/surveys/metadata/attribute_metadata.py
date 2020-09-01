from pandas import DataFrame, notnull
from typing import List, Optional

from survey.surveys.metadata.mixins import Metadata


class AttributeMetadata(Metadata):

    def __init__(self, name: str, text: str, type_name: str,
                 ordered: bool = None, expression: str = None,
                 loop_variables: List[str] = None,
                 loop_expression: Optional[str] = None):
        """
        Create metadata for a user attribute.

        :param name: The name of the attribute.
        :param text: The text representation of the attribute in the survey
                     data.
        :param type_name: The type of the attribute.
        :param ordered: Whether the values of the attribute are ordered.
        :param expression: Optional regular expression for matching multiple
                           columns for the same attribute, or for matching
                           single columns that need renaming.
        :param loop_variables: A list of variables over which the original
                               attribute has been looped, this metadata
                               instance representing the metadata for one of
                               the loop instances.
        :param loop_expression: Regular expression for matching the particular
                                loop instance for a given attribute.
        """
        self.name = name
        self.text = text
        self.type_name = type_name
        self.ordered = ordered
        self.expression = expression if notnull(expression) else None
        self.loop_variables = loop_variables if loop_variables else []
        self.loop_expression = loop_expression

    @staticmethod
    def from_dataframe(data: DataFrame) -> List['AttributeMetadata']:
        """
        Create a list of AttributeMetadata's from a pandas DataFrame

        :param data: DataFrame containing columns with the names of
                     AttributeMetadata attributes.
        """
        attribute_metadatas: List[AttributeMetadata] = []
        for _, row in data.iterrows():
            init_dict = {
                'name': row['name'], 'text': row['text'],
                'type_name': row['type_name'],
                'ordered': True if row['ordered'] == True else False
            }
            if 'expression' in row.keys():
                init_dict['expression'] = row['expression']
            if 'loop_expression' in row.keys():
                init_dict['loop_expression'] = row['loop_expression']
            if (
                    'loop_variables' in row.keys() and
                    notnull(row['loop_variables'])
            ):
                init_dict['loop_variables'] = row['loop_variables'].split('\n')
            attribute_metadatas.append(AttributeMetadata(**init_dict))
        return attribute_metadatas
