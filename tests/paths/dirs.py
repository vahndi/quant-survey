from pathlib import Path

TEST_DIR = Path(__file__)
while TEST_DIR.name != 'tests':
    TEST_DIR = TEST_DIR.parent

TEST_DATA_DIR = TEST_DIR / 'test-data'
