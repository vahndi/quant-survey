from typing import Union

from survey.attributes import CountAttribute
from survey.attributes import PositiveMeasureAttribute
from survey.attributes import RespondentAttribute, SingleCategoryAttribute
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.mixins.data_types.numerical_1d_mixin import Numerical1dMixin
from survey.questions import SingleChoiceQuestion, MultiChoiceQuestion, \
    LikertQuestion, CountQuestion, PositiveMeasureQuestion
from survey.questions._abstract.question import Question

CategoricalQuestion = Union[CategoricalMixin, Question]
NumericalQuestion = Union[Numerical1dMixin, Question]
CategoricalAttribute = Union[CategoricalMixin, RespondentAttribute]
NumericalAttribute = Union[Numerical1dMixin, RespondentAttribute]

Categorical = Union[CategoricalQuestion, CategoricalAttribute]
Numerical = Union[NumericalQuestion, NumericalAttribute]

CategoricalAttributeTypes = [
    SingleCategoryAttribute
]
CategoricalQuestionTypes = [
    LikertQuestion,
    MultiChoiceQuestion,
    SingleChoiceQuestion
]
NumericalAttributeTypes = [
    CountAttribute,
    PositiveMeasureAttribute
]
NumericalQuestionTypes = [
    CountQuestion,
    LikertQuestion,
    PositiveMeasureQuestion
]
