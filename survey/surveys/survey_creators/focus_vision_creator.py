from collections import OrderedDict
from itertools import product
from re import match
from typing import List, Dict

from numpy import nan
from pandas import read_excel, DataFrame, Series, ExcelFile, concat, notnull, \
    isnull

from survey import Survey
from survey.groups.question_groups.count_question_group import \
    CountQuestionGroup
from survey.groups.question_groups.free_text_question_group import \
    FreeTextQuestionGroup
from survey.groups.question_groups.likert_question_group import \
    LikertQuestionGroup
from survey.groups.question_groups.multi_choice_question_group import \
    MultiChoiceQuestionGroup
from survey.groups.question_groups.positive_measure_question_group import \
    PositiveMeasureQuestionGroup
from survey.groups.question_groups.question_group import QuestionGroup
from survey.groups.question_groups.ranked_choice_question_group import \
    RankedChoiceQuestionGroup
from survey.groups.question_groups.single_choice_question_group import \
    SingleChoiceQuestionGroup
from survey.surveys.metadata.question_metadata import QuestionMetadata
from survey.surveys.survey_creators.base.survey_creator import SurveyCreator


class FocusVisionCreator(SurveyCreator):

    def read_survey_data(self):

        data = read_excel(self.survey_data_fn)
        data.columns = [column.replace(u'\xa0', u' ')
                        for column in data.columns]
        if self.pre_clean is not None:
            data = self.pre_clean(data)
        self.survey_data = data

    def _loop_variable_froms(self, variable_name: str) -> List[str]:

        return self.loop_mappings.loc[
            self.loop_mappings['loop_variable'] == variable_name, 'map_from'
        ].tolist()

    def _loop_variable_tos(self, variable_name: str) -> List[str]:

        return self.loop_mappings.loc[
            self.loop_mappings['loop_variable'] == variable_name, 'map_to'
        ].tolist()

    def _loop_variable_mappings(self, variable_name: str) -> Series:

        return self.loop_mappings.loc[
            self.loop_mappings['loop_variable'] == variable_name
        ].set_index('map_from')['map_to']

    def _create_looped_metadata(self, metadata_dict: dict) -> List[dict]:

        new_metadata_dicts: List[dict] = []
        expressions: DataFrame = self.loop_expressions.loc[
            self.loop_expressions['loop_name'] ==
            metadata_dict['loop_variables'], :
        ]
        loop_variables: List[str] = metadata_dict['loop_variables'].split('\n')
        # build lists of loop variable values
        loop_froms: List[list] = []
        for loop_variable in loop_variables:
            loop_froms.append(self._loop_variable_froms(loop_variable))
        # iterate over potential matching expressions
        for _, expression_data in expressions.iterrows():
            # iterate over product of loop variable values and check for
            # matching column(s)
            for loop_vals in product(*loop_froms):
                # create a new expression using the loop variable values
                loop_expression = expression_data['expression_builder']
                for l, loop_val in enumerate(loop_vals):
                    loop_expression = loop_expression.replace(
                        '{{' + loop_variables[l] + '}}', str(loop_val)
                    )
                # find columns matching the question expression and
                # loop expression
                match_cols = [column for column in self.survey_data.columns
                              if match(loop_expression, column)
                              and match(metadata_dict['expression'], column)]
                if len(match_cols) > 0:
                    # create new metadata dict
                    new_metadata = {k: v for k, v in metadata_dict.items()}
                    # build list of loop variable values to sub into question /
                    # attribute name
                    var_vals: List[str] = []
                    for loop_variable, loop_val in zip(
                            loop_variables, loop_vals
                    ):
                        loop_var_mappings = self._loop_variable_mappings(
                            loop_variable
                        )
                        var_vals.append(loop_var_mappings.loc[loop_val])
                    # create new name for metadata based on loop values
                    new_metadata['name'] = (
                            new_metadata['name'] + '__' + '__'.join(var_vals)
                    )
                    # assign loop expression to match columns against
                    new_metadata['loop_expression'] = loop_expression
                    new_metadata_dicts.append(new_metadata)
        return new_metadata_dicts

    def read_metadata(self):

        metadata = ExcelFile(self.metadata_fn)
        # read metadata
        questions_metadata = read_excel(metadata, 'questions')
        self.questions_metadata_original = questions_metadata
        attributes_metadata = read_excel(metadata, 'attributes')
        orders_metadata = read_excel(metadata, 'orders')
        if 'loop_mappings' in metadata.sheet_names:
            self.loop_mappings = read_excel(metadata, 'loop_mappings')
        if 'loop_expressions' in metadata.sheet_names:
            self.loop_expressions = read_excel(metadata, 'loop_expressions')
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
                # add shared orders to metadata
                if notnull(row['categories']):
                    q_name = row['name']
                    order_value = row['categories']
                    ordered_choices = orders_metadata[
                        orders_metadata['category'] == order_value
                        ].copy()
                    ordered_choices['category'] = q_name
                    orders_metadata = concat([orders_metadata, ordered_choices])
        # create looped questions
        if 'loop_variables' in questions_metadata.columns:
            questions_metadata_items = []
            for _, row in questions_metadata.iterrows():
                metadata_dict = row.to_dict()
                if notnull(metadata_dict['loop_variables']):
                    new_metadatas = self._create_looped_metadata(metadata_dict)
                    questions_metadata_items.extend(new_metadatas)
                    for new_metadata in new_metadatas:
                        q_name = new_metadata['name']
                        order_value = row['categories']
                        ordered_choices = orders_metadata[
                            orders_metadata['category'] == order_value
                            ].copy()
                        ordered_choices['category'] = q_name
                        orders_metadata = concat([
                            orders_metadata, ordered_choices
                        ])
                else:
                    questions_metadata_items.append(metadata_dict)
            questions_metadata = DataFrame(questions_metadata_items)
        # set member variables
        self.questions_metadata = questions_metadata
        self.attributes_metadata = attributes_metadata
        self.orders_metadata = orders_metadata

    def _get_single_column_data(
            self, question_metadata: QuestionMetadata
    ) -> Series:

        if question_metadata.expression is None:
            return self.survey_data[question_metadata.text]
        else:
            if not question_metadata.loop_expression:
                match_cols = [c for c in self.survey_data.columns
                              if match(question_metadata.expression, c)]
            else:
                match_cols = [c for c in self.survey_data.columns
                              if match(question_metadata.expression, c) and
                              match(question_metadata.loop_expression, c)]
            if len(match_cols) != 1:
                raise ValueError(
                    f'Did not match exactly one column for question:'
                    f' "{question_metadata.name}". '
                    f'Matched {len(match_cols)}.'
                )
            data = self.survey_data[match_cols[0]]
            data = data.rename(question_metadata.name)
            return data

    def _get_multi_choice_data(
            self, question_metadata: QuestionMetadata
    ) -> Series:

        # merge multi-choice questions to single column
        if question_metadata.expression is None:
            raise ValueError('Need a regular expression to match '
                             'MultiChoice question columns.')
        match_cols = [c for c in self.survey_data.columns
                      if match(question_metadata.expression, c)]
        if len(match_cols) == 0:
            raise ValueError(
                f'Could not match expression "{question_metadata.expression}" '
                f'for MultiChoice question "question_metadata"'
            )
        if notnull(question_metadata.loop_expression):
            match_cols = [c for c in match_cols
                          if match(question_metadata.loop_expression, c)]
        choices = self.survey_data[match_cols].copy(deep=True)

        def create_cell_data(row: Series):
            selected_values = [val for val in row.to_list()
                               if not val.startswith('NO TO:')]
            return '\n'.join(selected_values)

        null_rows = choices.notnull().sum(axis=1) == 0
        data = Series(data=nan, index=choices.index)
        data.loc[~null_rows] = choices.loc[~null_rows].apply(
            create_cell_data, axis=1
        )

        return Series(data=data, name=question_metadata.name)

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
                    'No implementation for FocusVision RankedChoice Questions'
                )

        # set index of respondent id
        new_survey_data = concat(new_columns, axis=1)
        new_survey_data.index = self.survey_data['record: Record number']
        new_survey_data.index.name = 'Respondent ID'

        self.survey_data = new_survey_data

    def format_survey_data(self):

        pass

    def _create_groups(self) -> Dict[str, QuestionGroup]:

        # create groups
        groups = {}
        for _, question_metadata in self.questions_metadata_original.iterrows():
            if isnull(question_metadata['loop_variables']):
                continue
            # get values for each loop variable
            loop_variables = question_metadata['loop_variables'].split('\n')
            loop_names_values = OrderedDict([
                (variable_name, self._loop_variable_tos(variable_name))
                for variable_name in loop_variables
            ])
            group_constructor = {
                'Count': CountQuestionGroup,
                'FreeText': FreeTextQuestionGroup,
                'Likert': LikertQuestionGroup,
                'MultiChoice': MultiChoiceQuestionGroup,
                'PositiveMeasure': PositiveMeasureQuestionGroup,
                'RankedChoice': RankedChoiceQuestionGroup,
                'SingleChoice': SingleChoiceQuestionGroup
            }[question_metadata['type_name']]
            if len(loop_variables) == 1:
                var_1 = loop_variables[0]
                # constructor =
                group = group_constructor({
                    loop_value: [
                        q for q in self.questions
                        if q.name == f"{question_metadata['name']}"
                                     f"__{loop_value}"][0]
                    for loop_value in loop_names_values[var_1]
                })
                groups[question_metadata['name']] = group
            elif len(loop_variables) == 2:
                var_1, var_2 = loop_variables
                outer_group_groups = {}
                for val_1 in loop_names_values[var_1]:
                    inner_group_questions = {}
                    for val_2 in loop_names_values[var_2]:
                        inner_group_questions[val_2] = [
                            q for q in self.questions
                            if q.name == f"{question_metadata['name']}"
                                         f"__{val_1}__{val_2}"
                        ][0]
                    outer_group_groups[val_1] = group_constructor(
                        inner_group_questions
                    )
                for val_2 in loop_names_values[var_2]:
                    inner_group_questions = {}
                    for val_1 in loop_names_values[var_1]:
                        inner_group_questions[val_1] = [
                            q for q in self.questions
                            if q.name == f"{question_metadata['name']}" \
                                         f"__{val_1}__{val_2}"
                        ][0]
                    outer_group_groups[val_2] = group_constructor(
                        inner_group_questions
                    )
                groups[question_metadata['name']] = QuestionGroup(
                    outer_group_groups
                )
            else:
                print("Warning - can't set dynamic group for nested loops with"
                      " more than 2 loop variables.")
        return groups

    def create_survey(self):

        groups = self._create_groups()
        self.survey = Survey(
            name=self.survey_name,
            data=self.survey_data,
            questions=self.questions,
            respondents=self.respondents,
            attributes=self.respondent_attributes,
            groups=groups
        )
