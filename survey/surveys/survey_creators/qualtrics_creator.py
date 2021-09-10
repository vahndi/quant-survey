from pandas import DataFrame, read_csv, Series
from re import match

from survey.constants import CATEGORY_SPLITTER
from survey.surveys.metadata.question_metadata import QuestionMetadata
from survey.surveys.survey_creators.base.survey_creator import SurveyCreator


class QualtricsCreator(SurveyCreator):

    def read_survey_data(self):

        data = read_csv(self.survey_data_fn, header=1).iloc[1:]
        if self.pre_clean is not None:
            data = self.pre_clean(data)
        self.survey_data = data

    @staticmethod
    def _get_ranked_choice_name(column_name: str) -> str:

        re_ranked_choice = r'\w+ - (.+)'
        m = match(re_ranked_choice, column_name)
        return m.groups()[0]

    def _get_multi_choice_data(
            self, question_metadata: QuestionMetadata
    ) -> Series:

        # merge multi-choice questions to single column
        if question_metadata.expression is None:
            raise ValueError(
                'Need a regular expression to match '
                'MultiChoice question columns.'
            )
        match_cols = [c for c in self.survey_data.columns
                      if match(question_metadata.expression, c)]
        if len(match_cols) == 0:
            raise ValueError(
                f'Could not match expression "{question_metadata.expression}" '
                f'for MultiChoice question "{question_metadata}"'
            )
        return self.survey_data[match_cols].apply(
            lambda row: CATEGORY_SPLITTER.join(row.dropna().astype(str)), axis=1
        )

    def _get_ranked_choice_data(
            self, question_metadata: QuestionMetadata
    ) -> list:

        # merge ranked choice questions to single column
        if question_metadata.expression is None:
            raise ValueError(
                'Need a regular expression to match '
                'RankedChoice question columns.'
            )
        match_cols = [c for c in self.survey_data.columns
                      if match(question_metadata.expression, c)]
        choices = [self._get_ranked_choice_name(c) for c in match_cols]
        # create column in new dataframe
        new_answers = []
        for _, row in self.survey_data[match_cols].iterrows():
            # order choices by rank
            ranks = row.tolist()
            ranked_choices = [choice for rank, choice in
                              sorted(zip(ranks, choices))]
            ranked_choices = CATEGORY_SPLITTER.join(
                str(choice) for choice in ranked_choices
            )
            new_answers.append(ranked_choices)
        return new_answers

    def clean_survey_data(self):

        survey_data = self.survey_data
        new_survey_data = DataFrame()

        # copy attribute columns to new dataframe
        for amd in self.attribute_metadatas:
            new_survey_data[amd.text] = survey_data[amd.text]

        for qmd in self.question_metadatas:
            if qmd.type_name not in ('MultiChoice', 'RankedChoice'):
                new_survey_data[qmd.text] = self._get_single_column_data(qmd)
            elif qmd.type_name == 'MultiChoice':
                new_survey_data[qmd.text] = self._get_multi_choice_data(qmd)
            elif qmd.type_name == 'RankedChoice':
                new_survey_data[qmd.text] = self._get_ranked_choice_data(qmd)

        # set index of respondent id
        new_survey_data.index = self.survey_data['Response ID']

        self.survey_data = new_survey_data
