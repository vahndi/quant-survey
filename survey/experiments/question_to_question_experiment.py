from typing import Union

from survey.experiments._abstract.experiment import Experiment
from survey.experiments._abstract.mixins import SingleToSingleExperimentMixin, \
    SingleChoiceQuestionDependentMixin, SingleChoiceQuestionIndependentMixin
from survey.questions import SingleChoiceQuestion
from survey.surveys.survey import Survey


class QuestionToQuestionExperiment(
    SingleToSingleExperimentMixin,
    SingleChoiceQuestionDependentMixin,
    SingleChoiceQuestionIndependentMixin,
    Experiment
):

    def __init__(self, survey: Survey,
                 dependent: Union[str, SingleChoiceQuestion],
                 independent: Union[str, SingleChoiceQuestion]):
        """
        Create a new Experiment to find significance of dependent responses
        given independent responses.

        :param dependent: The dependent question to consider.
        :param independent: The independent question to use.
        """
        self._survey = survey
        self.set_values(
            survey=survey,
            dependent=dependent,
            independent=independent
        )
        self._results = []

    def __repr__(self):

        return (
            f'QuestionToQuestionExperiment('
            f'\n\tsurvey={self._survey.name},'
            f'\n\tdependent_question={self._dependent.name},'
            f'\n\tindependent_question={self._independent.name}'
            f'\n)'
        )
