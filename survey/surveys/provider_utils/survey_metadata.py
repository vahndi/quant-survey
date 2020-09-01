from collections import OrderedDict
from pandas import DataFrame, read_excel, read_csv, Series
from pathlib import Path
from re import match
from typing import Union


class SurveyMetadataMixin(object):

    data: DataFrame

    def header_info(self) -> DataFrame:
        """
        Return a dataframe with information extracted from the header of the
        survey data file.
        """
        raise NotImplementedError

    def get_column(self, column_name: str) -> Series:

        return self.data[column_name]

    def unique_answers(self, max_unique: int = 20) -> DataFrame:
        """
        Return a dataframe 'question_name' and 'question_answer' columns for
        each unique answer in questions where
        the number of answers is ≤ max_unique.
        """
        unique_values = []
        for _, column_info in self.header_info().iterrows():
            uniques = self.get_column(
                column_info['column_name']
            ).unique().tolist()
            if len(uniques) <= max_unique:
                for unique in uniques:
                    unique_values.append({
                        'question_text': column_info['question_text'],
                        'answer_value': unique
                    })
        return DataFrame(unique_values)[['question_text', 'answer_value']]


class AlphaHQMetadata(SurveyMetadataMixin, object):

    def __init__(self, file_name: Union[str, Path]):

        self.data: DataFrame = read_csv(file_name)

    def header_info(self) -> DataFrame:

        results = []
        for column in self.data.columns:
            column_info = {'column_name': column,
                           'question_text': column}
            results.append(column_info)
        return DataFrame(results)


class FocusVisionMetadata(SurveyMetadataMixin, object):

    RE_UNNUMBERED = r'^([a-zA-Z]+): (.+)$'
    RE_NUMBERED = r'^([a-zA-Z]+\d+): (.+)$'
    RE_CHOICE = r'^([a-zA-Z]+\d+)([a-zA-Z]+\d+): (.+) - (.+)\.{3}$'

    COLUMN_REGEXES = OrderedDict([
        (RE_UNNUMBERED, ('question_code', 'question_text')),
        (RE_NUMBERED, ('question_code', 'question_text')),
        (RE_CHOICE, ('question_code', 'answer_code',
                     'answer_value', 'question_text'))
    ])

    def __init__(self, file_name: Union[str, Path]):

        self.data: DataFrame = read_excel(file_name)

    def header_info(self) -> DataFrame:

        results = []
        for column in self.data.columns:
            for regex, group_names in self.COLUMN_REGEXES.items():
                m = match(regex, column)
                if m:
                    column_info = {'column_name': column}
                    groups = m.groups()
                    for g, group_name in enumerate(group_names):
                        column_info[group_name] = groups[g]
                    results.append(column_info)
                    break
        return DataFrame(results).fillna('')


class QualtricsMetadata(SurveyMetadataMixin, object):

    # row 1
    RE_ATTRIBUTE = r'^([a-zA-Z\(\) ]+)$'  # e.g. Duration (in seconds)
    RE_SINGLE_CHOICE_GROUPED = r'^Q(\d+.\d+)$'  # e.g. 'Q10.1'
    RE_MULTI_CHOICE = r'^Q(\d+)_(\d+)$'  # e.g. Q08_8
    RE_REASON_TEXT = r'^Q(\d+_\d+)_TEXT$'  # e.g. Q01_7_TEXT
    RE_SINGLE_CHOICE = r'^Q(\d+)$'  # e.g. 'Q41'
    # row 2
    RE_MULTI_CHOICE_NUMBER = r'^(\w+) - (.+)$'  # e.g. UsedItems - Thermal bag - small and/or large
    RE_QUESTION = r'^([a-zA-Z\(\) ]+)$'

    COLUMN_REGEXES_ROW_1 = OrderedDict([
        (RE_ATTRIBUTE, ('question_code',)),
        (RE_SINGLE_CHOICE_GROUPED, ('question_code',)),
        (RE_MULTI_CHOICE, ('question_code', 'question_sub_code')),
        (RE_REASON_TEXT, ('question_code',)),
        (RE_SINGLE_CHOICE, ('question_code',)),
    ])
    COLUMN_REGEXES_ROW_2 = OrderedDict([
        (RE_MULTI_CHOICE_NUMBER, ('question_text', 'answer_value')),
        (RE_QUESTION, ('question_text',))
    ])

    def __init__(self, file_name: Union[str, Path]):

        self.data: DataFrame = read_csv(file_name, header=[0, 1, 2])

    def get_column(self, column_name: str) -> Series:

        return self.data[
            [c for c in self.data.columns if c[1] == column_name][0]
        ]

    def header_info(self):

        results = []
        for column in self.data.columns:
            column_info = {'column_name': column[1]}
            m1 = None
            m2 = None
            for regex, group_names in self.COLUMN_REGEXES_ROW_1.items():
                m1 = match(regex, column[0])
                if m1:
                    groups = m1.groups()
                    for g, group_name in enumerate(group_names):
                        column_info[group_name] = groups[g]
                    break
            for regex, group_names in self.COLUMN_REGEXES_ROW_2.items():
                m2 = match(regex, column[1])
                if m2:
                    groups = m2.groups()
                    for g, group_name in enumerate(group_names):
                        column_info[group_name] = groups[g]
                    break
            if None in (m1, m2):
                continue
            results.append(column_info)

        return DataFrame(results).fillna('')


class UsabilityHubMetadata(SurveyMetadataMixin, object):

    RE_NORMAL_QUESTION = \
        r'^(\d+)\. \(([a-zA-Z ]+)\) \(Question (\d+): "(.+)"\) Answer$'
    RE_IMAGE_QUESTION = \
        r'^(\d+)\. \(([a-zA-Z ]+): \[(.+)\]\) \(Question (\d+): "(.+)"\) Answer$'
    RE_MATCH_ALL = r'^(.+)$'

    COLUMN_REGEXES = OrderedDict([
        (RE_NORMAL_QUESTION, ('page', 'section',
                              'question_code', 'question_text')),
        (RE_IMAGE_QUESTION, ('page', 'section', 'file_name',
                             'question_code', 'question_text')),
        (RE_MATCH_ALL, ('question_text',))
    ])

    def __init__(self, file_name: Union[str, Path]):

        self.data: DataFrame = read_csv(file_name)

    def header_info(self) -> DataFrame:

        results = []
        for column in self.data.columns:
            for regex, group_names in self.COLUMN_REGEXES.items():
                m = match(regex, column)
                if m:
                    column_info = {'column_name': column}
                    groups = m.groups()
                    for g, group_name in enumerate(group_names):
                        column_info[group_name] = groups[g]
                    results.append(column_info)
                    break
        return DataFrame(results).fillna('')
