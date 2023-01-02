from hyper_bump_it._cli import interactive
from hyper_bump_it._cli.interactive.top_level import TopMenu
from tests import sample_data as sd
from tests.conftest import ForceInput


def test_config_update__no_changes__same_config(force_input: ForceInput):
    force_input(TopMenu.Done.value)

    result = interactive.config_update(
        sd.SOME_VERSION, sd.some_config_file(), sd.SOME_PYPROJECT
    )

    assert result == (sd.some_config_file(), sd.SOME_PYPROJECT)
