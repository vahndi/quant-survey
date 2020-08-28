from numpy import nan
from pandas import Series, DataFrame, isnull
from typing import List

from survey.constants import CATEGORY_SPLITTER
from survey.surveys.metadata.question_metadata import QuestionMetadata
from survey.surveys.survey_creators.base.survey_creator import SurveyCreator


class AlphaHQCreator(SurveyCreator):

    def _get_multi_category_data(self, question_metadata: QuestionMetadata,
                                 categories: List[str]) -> Series:

        def get_selected(item: str):
            if isnull(item):
                return nan
            selected = []
            while len(item) > 0:
                for category in categories:
                    if item == category:
                        selected.append(category)
                        item = ''
                    elif item[: len(category) + 2] == category + '; ':
                        selected.append(category)
                        item = item[len(category) + 2:]
            return CATEGORY_SPLITTER.join(selected)

        data = self.survey_data[question_metadata.text]
        data = data.map(get_selected)
        return data

    def clean_survey_data(self):

        survey_data = self.survey_data
        new_survey_data = DataFrame()

        # copy attribute columns to new dataframe
        for amd in self.attribute_metadatas:
            new_survey_data[amd.text] = survey_data[amd.text]

        # copy (and rename) question columns to new dataframe
        for qmd in self.question_metadatas:
            if qmd.type_name not in ('MultiChoice', 'RankedChoice'):
                new_survey_data[qmd.text] = self._get_single_column_data(qmd)
            else:
                categories = self.orders_metadata.loc[
                    self.orders_metadata['category'] == qmd.name, 'value'
                ].tolist()
                if len(categories) == 0:
                    raise ValueError(
                        f'Error: Orders Metadata does not contain any values '
                        f'for "{qmd.name}".'
                    )
                new_survey_data[qmd.text] = self._get_multi_category_data(
                    question_metadata=qmd, categories=categories
                )

        self.survey_data = new_survey_data
