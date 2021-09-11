from re import match
from typing import List

from pandas import read_excel, DataFrame, Series, notnull, concat, ExcelFile, \
    isnull, pivot_table
from stringcase import snakecase

from survey import Survey
from survey.constants import CATEGORY_SPLITTER
from survey.surveys.metadata import QuestionMetadata, AttributeMetadata
from survey.surveys.survey_creators import SurveyCreator


class PollfishCreator(SurveyCreator):

    def read_survey_data(self):
        """
        Read the raw survey data file and do any custom pre-cleaning.
        """
        data = read_excel(self.survey_data_fn, sheet_name='Individuals')
        # fill in blank columns
        new_cols = []
        for col in data.columns:
            if col.startswith('Unnamed: '):
                new_cols.append(new_cols[-1])
            else:
                new_cols.append(col)
        data.columns = new_cols
        # pre-clean
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
        data = self.survey_data[question_metadata.text]
        if (
                question_metadata.type_name in (
                    'SingleChoice', 'SingleChoiceQuestion'
                ) and
                question_metadata.text in self.questions_metadata[
                    'text'].to_list()
        ):
            # replace other values
            def replace_other(value):
                if isnull(value):
                    return value
                else:
                    if value in categories:
                        return value
                    else:
                        return 'Other'

            metadata: Series = self.questions_metadata.loc[
                self.questions_metadata['text'] == question_metadata.text
            ].iloc[0]
            if 'other' in metadata.keys() and metadata['other'] == True:
                # do replacement
                category_name = metadata['categories']
                categories = self.orders_metadata.loc[
                    self.orders_metadata['category'] == category_name,
                    'value'
                ].to_list()
                data = data.apply(replace_other)
                # update categories in orders_metadata
                self.orders_metadata = self.orders_metadata.append(
                    Series({'category': question_metadata.name,
                            'value': 'Other'}),
                    ignore_index=True
                )

        return data

    def _get_multi_choice_data(
            self, question_metadata: QuestionMetadata
    ) -> Series:

        # get data
        data: DataFrame = self.survey_data[question_metadata.text]
        # replace other values
        if question_metadata.text in self.questions_metadata['text'].to_list():
            # this if condition excludes repeated questions that have had their
            # text changed
            def replace_other(value):
                if isnull(value):
                    return value
                else:
                    if value in categories:
                        return value
                    else:
                        return 'Other'

            metadata: Series = self.questions_metadata.loc[
                self.questions_metadata['text'] == question_metadata.text
            ].iloc[0]
            if 'other' in metadata.keys() and metadata['other'] == True:
                # do replacement
                category_name = metadata['categories']
                categories = self.orders_metadata.loc[
                    self.orders_metadata['category'] == category_name,
                    'value'
                ].to_list()
                data = data.applymap(replace_other)
                # update categories in orders_metadata
                self.orders_metadata = self.orders_metadata.append(
                    Series({'category': question_metadata.name,
                            'value': 'Other'}),
                    ignore_index=True
                )
        # merge multi-choice questions to single column
        return data.apply(
            lambda row: CATEGORY_SPLITTER.join(row.dropna().astype(str)),
            axis=1
        )

    def _get_ranked_choice_data(
            self, question_metadata: QuestionMetadata
    ) -> list:

        column = self.survey_data[question_metadata.text]

        def rank_choices(value: str):

            choices_ranks = value.split(' | ')
            choices = [rank_choice.split(':')[0]
                       for rank_choice in choices_ranks]
            ranks = [int(rank_choice.split(':')[1])
                     for rank_choice in choices_ranks]
            ranked_choices = [choice for rank, choice in
                              sorted(zip(ranks, choices))]
            return CATEGORY_SPLITTER.join(
                str(choice) for choice in ranked_choices
            )

        new_answers = column.map(rank_choices)
        return new_answers

    def convert_metadata_to_objects(self):
        """
        Convert DataFrames of metadata to lists of Metadata objects.
        """
        self.attribute_metadatas = AttributeMetadata.from_dataframe(
            self.attributes_metadata
        )
        rows: List[Series] = []
        for _, row in self.questions_metadata.iterrows():
            if notnull(row['repeat']):
                repeats = row['repeat'].split('\n')
                for repeat in repeats:
                    if row['type_name'] in (
                            'Likert', 'LikertQuestion',
                            'SingleChoice', 'SingleChoiceQuestion',
                            'MultiChoice', 'MultiChoiceQuestion'
                    ):
                        new_q_meta = row.copy(deep=True)
                        new_q_meta['name'] = (
                                row['name'] + '__' +
                                snakecase(repeat.title().replace(' ', ''))
                        )
                        new_q_meta['text'] = row['text'] + '\n' + repeat
                        rows.append(new_q_meta)
                    else:
                        print(row['name'])
                        raise TypeError(row['type_name'])
            else:
                rows.append(row)

        self.question_metadatas = QuestionMetadata.from_dataframe(
            DataFrame(rows)
        )

    def _create_repeated_single_column(self, metadata: Series):

        text = metadata['text']
        column = self.survey_data.loc[:, text]

        def create_cols_data(val: str):
            data_dict = {}
            if notnull(val):
                repeats_responses = val.split(' | ')
                for repeat_response in repeats_responses:
                    repeat, response = repeat_response.split(':')
                    data_dict[f'{text}\n{repeat}'] = response
            return data_dict
        data = DataFrame(column.map(create_cols_data).to_list())
        data.index = self.survey_data.index
        self.survey_data = concat([self.survey_data, data], axis=1)
        self.survey_data = self.survey_data.drop(text, axis=1)

    def _create_repeated_multi_column(self, metadata: Series):

        text = metadata['text']
        column: Series = self.survey_data.loc[:, text]
        new_datas = []
        for ix, value in column.items():
            if isnull(value):
                continue
            repeats_responses = value.split(' | ')
            for repeat_responses in repeats_responses:
                repeat, str_responses = repeat_responses.split(':')
                responses = str_responses.split(',')
                for response in responses:
                    new_datas.append({
                        'index': ix,
                        'question': f'{text}\n{repeat}\n{response}',
                        'response': response
                    })
        new_data = DataFrame(new_datas)
        pt = new_data.groupby([
            'index', 'question'])['response'].first().unstack('question')
        pt.columns = [
            '\n'.join(column.split('\n')[: -1])
            for column in pt.columns
        ]
        self.survey_data = concat([self.survey_data, pt], axis=1)
        self.survey_data = self.survey_data.drop(text, axis=1)

    def clean_survey_data(self):

        survey_data = self.survey_data
        new_survey_data = DataFrame()

        # copy attribute columns to new dataframe
        for amd in self.attribute_metadatas:
            new_survey_data[amd.text] = survey_data[amd.text]
        # rename columns tagged as multiple in metadata
        for _, row in self.questions_metadata.iterrows():
            if notnull(row['repeat']):
                if row['type_name'] in (
                        'Likert', 'LikertQuestion',
                        'SingleChoice', 'SingleChoiceQuestion'
                ):
                    self._create_repeated_single_column(row)
                elif row['type_name'] in (
                        'MultiChoice', 'MultiChoiceQuestion'
                ):
                    self._create_repeated_multi_column(row)
                else:
                    raise TypeError(f"Can't clean repeated {row['type_name']}")
        # create new columns
        for qmd in self.question_metadatas:
            if qmd.type_name not in ('MultiChoice', 'RankedChoice'):
                new_survey_data[qmd.text] = self._get_single_column_data(qmd)
            elif qmd.type_name == 'MultiChoice':
                new_survey_data[qmd.text] = self._get_multi_choice_data(qmd)
            elif qmd.type_name == 'RankedChoice':
                new_survey_data[qmd.text] = self._get_ranked_choice_data(qmd)

        # set index of respondent id
        new_survey_data.index = self.survey_data['ID']

        self.survey_data = new_survey_data


survey_data_fn = '/Users/vahndi.minah/Desktop/gitcode/dev/quant-survey/' \
                 'assets/surveys/pollfish/surveys/' \
                 'Pollfish_Example_Survey_253227526_en.xls'
metadata_fn = '/Users/vahndi.minah/Desktop/gitcode/dev/quant-survey/assets/' \
              'surveys/pollfish/metadata/survey-metadata.xlsx'


def create_survey() -> Survey:

    creator = PollfishCreator(
        survey_name='Example Survey',
        survey_data_fn=survey_data_fn,
        metadata_fn=metadata_fn,
    )
    return creator.run()


if __name__ == '__main__':

    srv = create_survey()
