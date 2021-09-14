from typing import List

from pandas import read_excel, DataFrame, Series, notnull, concat, isnull, \
    ExcelFile
from stringcase import snakecase

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
        # replace category values in original survey data
        questions = read_excel(self.metadata_fn, sheet_name='questions')
        attributes = read_excel(self.metadata_fn, sheet_name='attributes')
        questions = concat([questions, attributes])
        orders = read_excel(self.metadata_fn, sheet_name='orders')
        for _, question_data in questions.iterrows():
            category_name = question_data['categories']
            if isnull(category_name):
                continue
            question_cats = orders.loc[orders['category'] == category_name]
            question_cats = question_cats.dropna(subset=['replace_value'])
            if not len(question_cats):
                continue
            to_replace = question_cats.set_index('value')[
                'replace_value'].to_dict()
            type_name = question_data['type_name']
            if isnull(question_data['repeat']):
                if type_name in (
                        'SingleChoice', 'SingleChoiceQuestion',
                        'Likert', 'LikertQuestion',
                        'SingleCategory', 'SingleCategoryAttribute',
                        'MultiChoice', 'MultiChoiceQuestion'
                ):
                    data[question_data['text']] = data[
                        question_data['text']].replace(to_replace=to_replace)
                else:
                    raise TypeError(f'Cannot do value replacement '
                                    f'for type {type_name}')
            else:
                raise TypeError(f'Cannot do value replacement for repeat '
                                f'questions')
        # pre-clean
        if self.pre_clean is not None:
            data = self.pre_clean(data)

        self.survey_data = data

    def read_metadata(self):
        """
        Read the question, attribute and order metadata from the Excel
        metadata file.
        """
        metadata = ExcelFile(self.metadata_fn)
        # read metadata
        questions_metadata = read_excel(metadata, 'questions')
        attributes_metadata = read_excel(metadata, 'attributes')
        orders_metadata = read_excel(metadata, 'orders')
        # replace `value` with `replace_value` where applicable
        orders_metadata['value'] = orders_metadata.apply(
            lambda row: row['replace_value'] if notnull(row['replace_value'])
                        else row['value'],
            axis=1
        )
        # filter to unique(category, value)
        orders_metadata['value'] = orders_metadata['value'].astype(str)
        # convert to strings
        orders_metadata = orders_metadata.drop_duplicates(
            subset=['category', 'value'])
        # filter to specified survey
        if None not in (self.survey_id_col, self.survey_id):
            questions_metadata = self._filter_to_survey(questions_metadata)
            attributes_metadata = self._filter_to_survey(attributes_metadata)
            orders_metadata = self._filter_to_survey(orders_metadata)
        # check for clashes in question, attribute and category names
        category_names = sorted(orders_metadata['category'].unique())
        q_name_errors = []
        for q_name in sorted(questions_metadata['name'].unique()):
            if q_name in category_names:
                q_name_errors.append(q_name)
        if q_name_errors:
            raise ValueError(
                f'The following categories clash with question names. '
                f'Rename questions or categories.\n{q_name_errors}'
            )
        a_name_errors = []
        for a_name in sorted(attributes_metadata['name'].unique()):
            if a_name in category_names:
                a_name_errors.append(a_name)
        if a_name_errors:
            raise ValueError(
                f'The following categories clash with attribute names. '
                f'Rename attributes or categories.\n{a_name_errors}'
            )
        # create ordered choices for questions with shared choices
        for meta in (attributes_metadata, questions_metadata):
            for idx, row in meta.iterrows():
                if notnull(row['categories']):
                    q_name = row['name']
                    order_value = row['categories']
                    if q_name == order_value:
                        continue  # already assigned to the question
                    ordered_choices = orders_metadata[
                        orders_metadata['category'] == order_value
                        ].copy()
                    ordered_choices['category'] = q_name
                    orders_metadata = concat([orders_metadata, ordered_choices])
        # set member variables
        self.questions_metadata = questions_metadata
        self.attributes_metadata = attributes_metadata
        self.orders_metadata = orders_metadata

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
