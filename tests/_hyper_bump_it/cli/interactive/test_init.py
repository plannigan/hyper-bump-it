from hyper_bump_it._hyper_bump_it.cli import interactive
from hyper_bump_it._hyper_bump_it.cli.interactive.top_level import TopMenu
from tests._hyper_bump_it import sample_data as sd
from tests.conftest import ForceInput


def test_config_update__no_changes__same_config(force_input: ForceInput):
    force_input(TopMenu.Done.value)

    result = interactive.config_update(
        sd.some_config_file(), sd.SOME_PYPROJECT, sd.SOME_PROJECT_ROOT
    )

    assert result == (sd.some_config_file(), sd.SOME_PYPROJECT)
