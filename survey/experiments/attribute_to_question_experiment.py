from typing import Union

from survey.attributes import SingleCategoryAttribute
from survey.experiments._abstract.experiment import Experiment
from survey.experiments._abstract.mixins import (
    SingleToSingleExperimentMixin,
    SingleCategoryAttributeIndependentMixin,
    SingleChoiceQuestionDependentMixin
)
from survey.questions import SingleChoiceQuestion
from survey.surveys.survey import Survey


class AttributeToQuestionExperiment(
    SingleToSingleExperimentMixin,
    SingleCategoryAttributeIndependentMixin,
    SingleChoiceQuestionDependentMixin,
    Experiment
):

    def __init__(self, survey: Survey,
                 question: Union[str, SingleChoiceQuestion],
                 attribute: Union[str, SingleCategoryAttribute]):
        """
        Create a new Experiment to find significance of responses given
        attribute values.

        :param question: The question to consider.
        :param attribute: The attribute to use.
        """
        self._survey = survey
        self.set_values(
            survey=survey,
            dependent=question,
            independent=attribute
        )
        self._results = []

    @property
    def attribute(self):
        return self._independent

    @property
    def question(self):
        return self._dependent

    def __repr__(self):

        return (
            f'AttributeToQuestionExperiment('
            f'\n\tsurvey={self._survey.name},'
            f'\n\tquestion={self.question.name},'
            f'\n\tattribute={self.attribute.name}'
            f'\n)'
        )
