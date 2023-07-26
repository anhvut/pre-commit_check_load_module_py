import os

from check_load_module import main


def test_check_import():
    os.chdir(os.path.join(os.path.dirname(__file__), 'repo'))
    assert main(['app/app.py']) == 0
    assert main(['app/app.py', 'common/common1.py']) == 0
    assert main(['app/app.py', 'common/common1.py', 'common/common3.py']) == 1
