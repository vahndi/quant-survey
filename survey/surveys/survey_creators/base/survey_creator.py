from pandas import DataFrame, read_excel, ExcelFile, read_csv, concat, Series, \
    notnull
from pathlib import Path
from re import match
from typing import Optional, List, Union, Callable

from survey import Survey
from survey.attributes import PositiveMeasureAttribute
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.attributes import RespondentAttribute, SingleCategoryAttribute
from survey.attributes import CountAttribute
from survey.questions import Question
from survey.questions import SingleChoiceQuestion, FreeTextQuestion, \
    LikertQuestion, MultiChoiceQuestion
from survey.questions import CountQuestion
from survey.questions import PositiveMeasureQuestion
from survey.questions import RankedChoiceQuestion
from survey.respondents import Respondent
from survey.surveys.metadata.attribute_metadata import AttributeMetadata
from survey.surveys.metadata.question_metadata import QuestionMetadata
from survey.surveys.survey_creators.choices import get_choices, \
    get_likert_choices, get_multi_choices


class SurveyCreator(object):

    def __init__(self,
                 survey_name: str,
                 survey_data_fn: Union[str, Path],
                 metadata_fn: Union[str, Path],
                 survey_id_col: Optional[str] = None,
                 survey_id: Optional = None,
                 pre_clean: Optional[Callable[[DataFrame], DataFrame]] = None):
        """
        Create a new SurveyCreator.

        :param survey_name: Name for the survey.
        :param survey_data_fn: Path to the survey raw data file.
        :param metadata_fn: Path to the survey metadata file.
        :param survey_id_col: Optional name of the column that identifies the
                              survey in the metadata file.
        :param survey_id: Optional value that identifies the survey in the
                          metadata file.
        :param pre_clean: Optional method to run on the raw data file on read.
                          Used if there are some values in this specific raw
                          data file that need changing in some way.
        """
        # now
        self.survey_name: str = survey_name
        self.survey_data_fn: Path = (
            survey_data_fn if isinstance(survey_data_fn, Path)
            else Path(survey_data_fn)
        )
        self.metadata_fn: Path = (
            metadata_fn if isinstance(metadata_fn, Path)
            else Path(metadata_fn)
        )
        self.survey_id_col: Optional[str] = survey_id_col
        self.survey_id: Optional = survey_id
        self.survey: Optional[Survey] = None
        self.pre_clean = pre_clean

        # later
        self.survey_data: Optional[DataFrame] = None
        self.questions_metadata: Optional[DataFrame] = None
        self.attributes_metadata: Optional[DataFrame] = None
        self.orders_metadata: Optional[DataFrame] = None
        self.question_metadatas: Optional[List[QuestionMetadata]] = None
        self.attribute_metadatas: Optional[List[AttributeMetadata]] = None
        self.questions: Optional[List[Question]] = None
        self.respondent_attributes: Optional[List[RespondentAttribute]] = None
        self.respondents: Optional[List[Respondent]] = None

        # focus vision
        self.loop_mappings: Optional[DataFrame] = None
        self.loop_expressions: Optional[DataFrame] = None
        self.questions_metadata_original: Optional[DataFrame] = None

    def run(self) -> Survey:
        """
        Run all the steps to create the Survey object.
        """
        self.read_survey_data()
        self.read_metadata()
        self.validate_metadata()
        self.convert_metadata_to_objects()
        self.clean_survey_data()
        self.format_survey_data()
        self.create_survey_components()
        self.create_survey()
        return self.survey

    def read_survey_data(self):
        """
        Read the raw survey data file and do any custom pre-cleaning.
        """
        data = read_csv(self.survey_data_fn)
        if self.pre_clean is not None:
            data = self.pre_clean(data)
        self.survey_data = data

    def _filter_to_survey(self, metadata: DataFrame) -> DataFrame:
        """
        Filter the given metadata to only contain metadata for the current
        survey.
        """
        if self.survey_id_col in metadata.columns:
            metadata = metadata.loc[
                (metadata[self.survey_id_col] == self.survey_id) |
                (metadata[self.survey_id_col].isnull())
            ]
        return metadata

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
        orders_metadata['value'] = orders_metadata['value'].astype(str)
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
        # create ordered choices for questions and attributes with shared
        # choices
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

    def validate_metadata(self):
        """
        Check each order listed in question and attribute categories exists.
        """
        question_category_groups = (
            self.questions_metadata['categories'].dropna().unique()
        )
        attribute_category_groups = (
            self.attributes_metadata['categories'].dropna().unique()
        )
        missing_q_cats = []
        missing_a_cats = []
        categories = self.orders_metadata['category'].unique()
        for group in question_category_groups:
            if group not in categories:
                missing_q_cats.append(f'Question Category: {group}')
        for group in attribute_category_groups:
            if group not in categories:
                missing_a_cats.append(f'Attribute Category: {group}')
        missing_cats = missing_q_cats + missing_a_cats
        if len(missing_q_cats) or len(missing_a_cats):
            raise ValueError(
                'Categories listed in questions / attribute sheets'
                ' not present in orders sheet:\n' +
                '\n'.join(missing_cats)
            )

    def convert_metadata_to_objects(self):
        """
        Convert DataFrames of metadata to lists of Metadata objects.
        """
        self.attribute_metadatas = AttributeMetadata.from_dataframe(
            self.attributes_metadata
        )
        self.question_metadatas = QuestionMetadata.from_dataframe(
            self.questions_metadata
        )

    def _get_single_column_data(
            self,
            question_metadata: QuestionMetadata
    ) -> Series:
        """
        Find a single column using the QuestionMetadata and return as a Series.
        """
        if question_metadata.expression is None:
            return self.survey_data[question_metadata.text]
        else:
            match_cols = [c for c in self.survey_data.columns
                          if match(question_metadata.expression, c)]
            if len(match_cols) != 1:
                raise ValueError(
                    f'Expecting 1 match for expression '
                    f'{question_metadata.expression} '
                    f'but {len(match_cols)} were found.'
                )

            match_col = match_cols[0]
            return self.survey_data[match_col]

    def clean_survey_data(self):
        """
        Extract the data from the survey data file using the validated
        Metadata objects
        """
        survey_data = self.survey_data
        new_survey_data = DataFrame()

        # copy attribute columns to new dataframe
        for amd in self.attribute_metadatas:
            new_survey_data[amd.text] = survey_data[amd.text]

        # copy (and rename) question columns to new dataframe
        for qmd in self.question_metadatas:
            new_survey_data[qmd.text] = self._get_single_column_data(qmd)

        self.survey_data = new_survey_data

    def format_survey_data(self):
        """
        Rename columns from question and attribute text to python name.
        """
        survey_data = self.survey_data
        survey_data = survey_data.rename(
            columns=AttributeMetadata.text_to_name(self.attribute_metadatas)
        )
        survey_data = survey_data.rename(
            columns=QuestionMetadata.text_to_name(self.question_metadatas)
        )
        self.survey_data = survey_data

    # region creation

    @staticmethod
    def _create_questions(
            questions_meta: List[QuestionMetadata],
            survey_data: DataFrame, orders_meta: DataFrame
    ) -> List[Question]:
        """
        Create the SurveyQuestion objects.
        """
        questions: List[Question] = []
        prev_qname = ''
        for q_meta in questions_meta:
            if q_meta.name == prev_qname:
                continue
            elif q_meta.type_name in ('SingleChoice', 'SingleChoiceQuestion'):
                choices = get_choices(
                    orders_meta=orders_meta, survey_data=survey_data,
                    question_name=q_meta.name
                )
                questions.append(SingleChoiceQuestion(
                    name=q_meta.name, text=q_meta.text,
                    ordered=q_meta.ordered,
                    categories=choices
                ))
            elif q_meta.type_name in ('FreeText', 'FreeTextQuestion'):
                questions.append(FreeTextQuestion(
                    name=q_meta.name, text=q_meta.text,
                ))
            elif q_meta.type_name in ('Likert', 'LikertQuestion'):
                choices = get_likert_choices(
                    orders_meta=orders_meta, survey_data=survey_data,
                    question_name=q_meta.name
                )
                questions.append(LikertQuestion(
                    name=q_meta.name, text=q_meta.text,
                    categories=choices
                ))
            elif q_meta.type_name in ('MultiChoice', 'MultiChoiceQuestion'):
                choices = get_multi_choices(
                    orders_meta=orders_meta, survey_data=survey_data,
                    question_name=q_meta.name
                )
                questions.append(MultiChoiceQuestion(
                    name=q_meta.name, text=q_meta.text,
                    categories=choices, ordered=q_meta.ordered
                ))
            elif q_meta.type_name in ('RankedChoice', 'RankedChoiceQuestion'):
                choices = get_multi_choices(
                    orders_meta=orders_meta, survey_data=survey_data,
                    question_name=q_meta.name
                )
                questions.append(RankedChoiceQuestion(
                    name=q_meta.name, text=q_meta.text,
                    categories=choices
                ))
            elif q_meta.type_name in ('Count', 'CountQuestion'):
                questions.append(CountQuestion(
                    name=q_meta.name, text=q_meta.text
                ))
            elif q_meta.type_name in ('PositiveMeasure',
                                      'PositiveMeasureQuestion'):
                questions.append(PositiveMeasureQuestion(
                    name=q_meta.name, text=q_meta.text
                ))
            else:
                raise ValueError(
                    f'Question Type "{q_meta.type_name}" is not supported'
                )
            prev_qname = q_meta.name
        # clean up string answers
        for question in questions:
            if (
                    isinstance(question, CategoricalMixin) and
                    isinstance(question, Question)
            ):
                survey_data[question.name] = survey_data[question.name].map(
                    lambda v: v.strip() if type(v) is str else v
                )
        return questions

    @staticmethod
    def _create_respondent_attributes(
            attributes_meta: List[AttributeMetadata],
            survey_data: DataFrame, orders_meta: DataFrame
    ) -> List[RespondentAttribute]:
        """
        Create the RespondentAttribute objects.
        """
        respondent_attributes = []
        for a_meta in attributes_meta:
            if a_meta.type_name in ('SingleCategory',
                                    'SingleCategoryAttribute'):
                choices = get_choices(
                    orders_meta=orders_meta, survey_data=survey_data,
                    question_name=a_meta.name
                )
                respondent_attributes.append(SingleCategoryAttribute(
                    name=a_meta.name, text=a_meta.text,
                    ordered=a_meta.ordered,
                    categories=choices
                ))
            elif a_meta.type_name in ('Count', 'CountAttribute'):
                respondent_attributes.append(CountAttribute(
                    name=a_meta.name, text=a_meta.text
                ))
            elif a_meta.type_name in ('PositiveMeasure',
                                      'PositiveMeasureAttribute'):
                respondent_attributes.append(PositiveMeasureAttribute(
                    name=a_meta.name, text=a_meta.text
                ))
            else:
                raise ValueError(
                    f'Attribute Type "{a_meta.type_name}" is not supported'
                )
        return respondent_attributes

    @staticmethod
    def _create_respondents(
            survey_data: DataFrame,
            attributes_meta: List[AttributeMetadata]
    ) -> List[Respondent]:
        """
        Create the Respondent attributes.
        """
        # TODO: this may throw a reindex on duplicate index if there is an
        #  attribute with the same name as a question
        respondents = []
        for ix, row in survey_data.iterrows():
            respondent_attrs = row.reindex([
                a_meta.name for a_meta in attributes_meta
            ]).to_dict()
            respondents.append(Respondent(
                respondent_id=ix,
                attributes=respondent_attrs
            ))
        return respondents

    # end region

    def create_survey_components(self):
        """
        Create the Question, RespondentAttribute and Respondent objects.
        """
        self.questions = self._create_questions(
            questions_meta=self.question_metadatas,
            survey_data=self.survey_data,
            orders_meta=self.orders_metadata
        )
        self.respondent_attributes = self._create_respondent_attributes(
            attributes_meta=self.attribute_metadatas,
            survey_data=self.survey_data,
            orders_meta=self.orders_metadata
        )
        self.respondents = self._create_respondents(
            survey_data=self.survey_data,
            attributes_meta=self.attribute_metadatas
        )

    def create_survey(self):
        """
        Create the Survey from the previously created Questions, Attributes and
        Respondents, and the cleaned data.
        """
        self.survey = Survey(
            name=self.survey_name,
            data=self.survey_data,
            questions=self.questions,
            respondents=self.respondents,
            attributes=self.respondent_attributes
        )
