from numpy import nan
from pandas import Series, MultiIndex, Index
from random import choices, seed

from survey.utils.data_frames import count_coincidences

seed(0)

gender = Series(
    index=Index(data=range(1, 101), name='Respondent ID'),
    data=choices(['Female', 'Male'], weights=[0.5, 0.5], k=100),
    name='gender'
)
symptoms = Series(
    index=Index(data=range(1, 101), name='Respondent ID'),
    data=nan, name='symptoms'
)
symptoms[gender == 'Male'] = choices(
    population=['headache', 'fever', 'cough'],
    weights=[0.5, 0.3, 0.2],
    k=len(symptoms[gender == 'Male'])
)
symptoms[gender == 'Female'] = choices(
    population=['headache', 'fever', 'cough'],
    weights=[0.1, 0.4, 0.5],
    k=len(symptoms[gender == 'Female'])
)
symptoms_stacked = Series(
    data=symptoms.values, name='symptoms',
    index=MultiIndex.from_tuples(
        tuples=[(ix, 'aspirin') for ix in range(1, 51)] +
               [(ix, 'paracetamol') for ix in range(26, 76)],
        names=['Respondent ID', 'medication']
    )
)
gender_stacked = Series(
    data=gender.values, name='gender',
    index=MultiIndex.from_tuples(
        tuples=[(ix, 'aspirin') for ix in range(11, 61)] +
               [(ix, 'paracetamol') for ix in range(36, 86)],
        names=['Respondent ID', 'medication']
    )
)

print('\nsimple-simple')
coincidences = count_coincidences(
    gender.copy(), symptoms.copy(),
    'gender', 'symptoms',
    ['Female', 'Male'], ['cough', 'fever', 'headache']
)
print(coincidences)

print('\nsimple-stacked')
coincidences = count_coincidences(
    gender.copy(), symptoms_stacked.copy(),
    'gender', 'symptoms',
    ['Female', 'Male'], ['cough', 'fever', 'headache']
)
print(coincidences)

print('\nstacked-simple')
coincidences = count_coincidences(
    gender_stacked.copy(), symptoms.copy(),
    'gender', 'symptoms',
    ['Female', 'Male'], ['cough', 'fever', 'headache']
)
print(coincidences)

print('\nstacked-stacked')
coincidences = count_coincidences(
    gender_stacked.copy(), symptoms_stacked.copy(),
    'gender', 'symptoms',
    ['Female', 'Male'], ['cough', 'fever', 'headache']
)
print(coincidences)
