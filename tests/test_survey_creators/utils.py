from pathlib import Path

proj_path = __file__

while Path(proj_path).name != 'quant-survey':
    proj_path = Path(proj_path).parent
assets_path = proj_path / 'assets'
surveys_path = assets_path / 'surveys'


def get_surveys_dir(provider_name: str) -> Path:

    provider_path = surveys_path / provider_name
    surveys_dir = provider_path / 'surveys'
    return surveys_dir


def get_metadata_path(provider_name: str) -> str:

    provider_path = surveys_path / provider_name
    metadata_path = list((provider_path / 'metadata').glob('*.xlsx'))[0]
    return str(metadata_path)
