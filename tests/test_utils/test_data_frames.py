from numpy import nan
from pandas import Series, MultiIndex, Index
from random import choices, seed
from unittest.case import TestCase

from survey.utils.data_frames import count_coincidences


class TestDataFrames(TestCase):

    def setUp(self) -> None:

        seed(0)
        self.gender = Series(
            index=Index(data=range(1, 101), name='Respondent ID'),
            data=choices(['Female', 'Male'], weights=[0.5, 0.5], k=100),
            name='gender'
        )
        self.symptoms = Series(
            index=Index(data=range(1, 101), name='Respondent ID'),
            data=nan, name='symptoms'
        )
        self.symptoms[self.gender == 'Male'] = choices(
            population=['headache', 'fever', 'cough'],
            weights=[0.5, 0.3, 0.2],
            k=len(self.symptoms[self.gender == 'Male'])
        )
        self.symptoms[self.gender == 'Female'] = choices(
            population=['headache', 'fever', 'cough'],
            weights=[0.1, 0.4, 0.5],
            k=len(self.symptoms[self.gender == 'Female'])
        )
        self.symptoms_stacked = Series(
            data=self.symptoms.values, name='symptoms',
            index=MultiIndex.from_tuples(
                tuples=[(ix, 'aspirin') for ix in range(1, 51)] +
                       [(ix, 'paracetamol') for ix in range(26, 76)],
                names=['Respondent ID', 'medication']
            )
        )
        self.gender_stacked = Series(
            data=self.gender.values, name='gender',
            index=MultiIndex.from_tuples(
                tuples=[(ix, 'aspirin') for ix in range(11, 61)] +
                       [(ix, 'paracetamol') for ix in range(36, 86)],
                names=['Respondent ID', 'medication']
            )
        )

    def test_count_coincidences_simple_simple(self):
        """
        for cpts and jpts between 2 unstacked distributions
        """
        coincidences = count_coincidences(
            data_1=self.gender, data_2=self.symptoms,
            column_1='gender', column_2='symptoms',
            column_1_order=['Female', 'Male'],
            column_2_order=['cough', 'fever', 'headache']
        )
        self.assertEqual(15, coincidences.loc['cough', 'Female'])
        self.assertEqual(18, coincidences.loc['fever', 'Female'])
        self.assertEqual(4, coincidences.loc['headache', 'Female'])
        self.assertEqual(12, coincidences.loc['cough', 'Male'])
        self.assertEqual(17, coincidences.loc['fever', 'Male'])
        self.assertEqual(34, coincidences.loc['headache', 'Male'])

    def test_count_coincidences_simple_stacked(self):

        coincidences = count_coincidences(
            data_1=self.gender, data_2=self.symptoms_stacked,
            column_1='gender', column_2='symptoms',
            column_1_order=['Female', 'Male'],
            column_2_order=['cough', 'fever', 'headache']
        )
        self.assertEqual(12, coincidences.loc['cough', 'Female'])
        self.assertEqual(18, coincidences.loc['fever', 'Female'])
        self.assertEqual(13, coincidences.loc['headache', 'Female'])
        self.assertEqual(15, coincidences.loc['cough', 'Male'])
        self.assertEqual(17, coincidences.loc['fever', 'Male'])
        self.assertEqual(25, coincidences.loc['headache', 'Male'])

    def test_count_coincidences_stacked_simple(self):

        coincidences = count_coincidences(
            data_1=self.gender_stacked, data_2=self.symptoms,
            column_1='gender', column_2='symptoms',
            column_1_order=['Female', 'Male'],
            column_2_order=['cough', 'fever', 'headache']
        )
        self.assertEqual(16, coincidences.loc['cough', 'Female'])
        self.assertEqual(7, coincidences.loc['fever', 'Female'])
        self.assertEqual(14, coincidences.loc['headache', 'Female'])
        self.assertEqual(15, coincidences.loc['cough', 'Male'])
        self.assertEqual(23, coincidences.loc['fever', 'Male'])
        self.assertEqual(25, coincidences.loc['headache', 'Male'])

    def test_count_coincidences_stacked_stacked(self):
        """
        for cpts and jpts between 2 stacked distributions
        """
        coincidences = count_coincidences(
            data_1=self.gender_stacked, data_2=self.symptoms_stacked,
            column_1='gender', column_2='symptoms',
            column_1_order=['Female', 'Male'],
            column_2_order=['cough', 'fever', 'headache']
        )
        self.assertEqual(9, coincidences.loc['cough', 'Female'])
        self.assertEqual(7, coincidences.loc['fever', 'Female'])
        self.assertEqual(12, coincidences.loc['headache', 'Female'])
        self.assertEqual(10, coincidences.loc['cough', 'Male'])
        self.assertEqual(22, coincidences.loc['fever', 'Male'])
        self.assertEqual(20, coincidences.loc['headache', 'Male'])
