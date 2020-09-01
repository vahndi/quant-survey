from typing import List, Optional

from pandas import DataFrame, notnull

from survey.surveys.metadata.mixins import Metadata


class QuestionMetadata(Metadata):

    def __init__(self, name: str, text: str, type_name: str,
                 ordered: bool = None, expression: str = None,
                 loop_variables: List[str] = None, loop_expression: Optional[str] = None):
        """
        Create a new QuestionMetadata.

        :param name: Name of the question - should be a valid python variable
                     name.
        :param text: The actual text of the question asked.
        :param type_name: The type of the question.
                          One of `['Count', 'FreeText', 'Likert',
                          'MultiChoice', 'PositiveMeasure', 'RankedChoice',
                          'SingleChoice']`
        :param ordered: For Likert, SingleChoice and MultiChoice questions,
                        whether the answers are in a specific order.
        :param expression: Optional regular expression for matching multiple
                           columns for the same question, or for matching
                           single columns that need renaming.
        :param loop_variables: A list of variables over which the original
                               question has been looped, this metadata
                               instance representing the metadata for one of the
                               loop instances.
        :param loop_expression: Regular expression for matching the particular
                                loop instance for a given question.
        """
        self.name = name
        self.text = text
        self.type_name = type_name
        self.ordered = ordered if notnull(ordered) else None
        self.expression = expression if notnull(expression) else None
        self.loop_variables = loop_variables if loop_variables else []
        self.loop_expression = loop_expression

    @staticmethod
    def from_dataframe(data: DataFrame) -> List['QuestionMetadata']:
        """
        Create a list of QuestionMetadata's from a pandas DataFrame

        :param data: DataFrame containing columns with the names of
                     QuestionMetadata attributes.
        """
        question_metadatas: List[QuestionMetadata] = []
        for _, row in data.iterrows():
            init_dict = {
                'name': row['name'], 'text': row['text'],
                'type_name': row['type_name'],
                'ordered':  True if row['ordered'] == True else False,
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
            question_metadatas.append(QuestionMetadata(**init_dict))
        return question_metadatas
