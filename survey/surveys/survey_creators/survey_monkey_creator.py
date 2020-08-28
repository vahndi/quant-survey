from re import match

from numpy import nan
from pandas import read_excel, Series, concat, MultiIndex, notnull

from survey.constants import CATEGORY_SPLITTER
from survey.surveys.metadata import QuestionMetadata
from survey.surveys.survey_creators import SurveyCreator


class SurveyMonkeyCreator(SurveyCreator):
    """
    N.B. Based on the "condensed" Excel Individual Responses download format.
    """
    def read_survey_data(self):

        data = read_excel(self.survey_data_fn, header=(0, 1))
        level_0 = data.columns.get_level_values(0).to_series()
        level_1 = data.columns.get_level_values(1).to_series()
        level_1 = level_1.map(lambda x: '' if x.startswith('Unnamed: ') else x)
        data.columns = MultiIndex.from_tuples(
            tuples=[(l0, l1) for l0, l1 in zip(
                level_0.to_list(), level_1.to_list()
            )]
        )
        if self.pre_clean is not None:
            data = self.pre_clean(data)
        self.survey_data = data

    def _get_single_column_data(
            self,
            question_metadata: QuestionMetadata
    ) -> Series:
        """
        Find a single column using the QuestionMetadata and return as a Series.
        """
        level_0 = self.survey_data.columns.get_level_values(0).to_list()
        level_1 = self.survey_data.columns.get_level_values(1).to_list()
        if question_metadata.expression is None:
            match_cols = [(l0, l1) for l0, l1 in zip(level_0, level_1)
                          if l0 == question_metadata.text]
        else:
            match_cols = [(l0, l1) for l0, l1 in zip(level_0, level_1)
                          if match(question_metadata.expression, l0)]
        if len(match_cols) == 2:  # 2nd column is Other (Please Specify)
            return Series(
                index=self.survey_data.index,
                name=match_cols[0][0],
                data=[c0 if notnull(c0) else 'Other'
                      for c0, c1 in zip(
                          self.survey_data[match_cols[0]].to_list(),
                          self.survey_data[match_cols[1]].to_list()
                      )]
            )
        elif len(match_cols) != 1:
            raise ValueError(
                f'Expecting 1 or 2 matches for expression '
                f'{question_metadata.expression} '
                f'but {len(match_cols)} were found.'
            )

        match_col = match_cols[0]
        return Series(
            name=match_col[0],
            index=self.survey_data.index,
            data=self.survey_data[match_col].values
        )

    def _get_multi_choice_data(
            self, question_metadata: QuestionMetadata
    ) -> Series:

        # merge multi-choice questions to single column
        level_0 = self.survey_data.columns.get_level_values(0).to_list()
        level_1 = self.survey_data.columns.get_level_values(1).to_list()
        if question_metadata.expression is None:
            match_cols = [(l0, l1) for l0, l1 in zip(level_0, level_1)
                          if l0 == question_metadata.text]
        else:
            match_cols = [(l0, l1) for l0, l1 in zip(level_0, level_1)
                          if match(question_metadata.expression, l0)]
        if len(match_cols) == 0:
            if question_metadata.expression is None:
                raise ValueError(
                    f'Could not find any columns matching '
                    f'"{question_metadata.text}"'
                )
            else:
                raise ValueError(
                    f'Could not match expression '
                    f'"{question_metadata.expression}" '
                    f'for MultiChoice question "{question_metadata}"'
                )
        return Series(
            name=match_cols[0][0],
            index=self.survey_data.index,
            data=self.survey_data[match_cols].apply(
                         lambda row: CATEGORY_SPLITTER.join(
                             row.dropna().astype(str)
                         ) if len(row.dropna()) else nan,
                axis=1)
        )

    def clean_survey_data(self):

        new_columns = []
        # copy attribute columns to new dataframe
        for amd in self.attribute_metadatas:
            new_columns.append(self._get_single_column_data(amd))

        for qmd in self.question_metadatas:
            if qmd.type_name not in ('MultiChoice', 'RankedChoice'):
                new_columns.append(self._get_single_column_data(qmd))
            elif qmd.type_name == 'MultiChoice':
                new_columns.append(self._get_multi_choice_data(qmd))
            elif qmd.type_name == 'RankedChoice':
                raise NotImplementedError(
                    'No implementation for SurveyMonkey RankedChoice Questions'
                )

        # set index of respondent id
        new_survey_data = concat(new_columns, axis=1)
        new_survey_data.index = self.survey_data[('Respondent ID', '')]
        new_survey_data.index.name = 'Respondent ID'

        self.survey_data = new_survey_data
