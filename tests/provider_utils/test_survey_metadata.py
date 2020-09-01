from survey.surveys.provider_utils.survey_metadata import AlphaHQMetadata, FocusVisionMetadata, QualtricsMetadata, \
    UsabilityHubMetadata
from tests.test_survey_creators.utils import get_surveys_dir


def test_alpha_hq_metadata():

    fp = get_surveys_dir('alpha_hq') / 'test_69_data.csv'
    metadata = AlphaHQMetadata(fp)
    info = metadata.header_info()
    uniques = metadata.unique_answers()
    return info, uniques


def test_focus_vision_metadata():

    fp = get_surveys_dir('focus_vision') / 'Sample Raw Data (Text).xlsx'
    metadata = FocusVisionMetadata(fp)
    info = metadata.header_info()
    uniques = metadata.unique_answers()
    return info, uniques


def test_qualtrics_metadata():

    fp = get_surveys_dir('qualtrics') / f'test_Kit_ENGLISH_AUSTRALIA_May+5,' \
                                        f'+2019_18.36.csv'
    metadata = QualtricsMetadata(fp)
    info = metadata.header_info()
    uniques = metadata.unique_answers()
    return info, uniques


def test_usability_hub_metadata():

    fp = get_surveys_dir('usability_hub') / f'test Demo ' \
                                            f'Survey-results_cleaned.csv'
    metadata = UsabilityHubMetadata(fp)
    info = metadata.header_info()
    uniques = metadata.unique_answers()
    return info, uniques


if __name__ == '__main__':

    # i, u = test_alpha_hq_metadata()
    i, u = test_focus_vision_metadata()
    # i, u = test_qualtrics_metadata()
    # i, u = test_usability_hub_metadata()

