import pytest

from hyper_bump_it._hyper_bump_it.version import Version, _Alpha, _Numeric
from tests._hyper_bump_it import sample_data as sd


@pytest.mark.parametrize(
    ["description", "version_text"],
    [
        ("empty string", ""),
        ("no minor or patch", "1"),
        ("no patch", "1.2"),
        ("bad numeric perpetrator", "1-2-3"),
        ("bad major character", "1a.2.3"),
        ("bad minor character", "1.2b.3"),
        ("bad patch character", "1.2.3c"),
        ("negative major", "-1.2.3"),
        ("negative minor", "1.-2.3"),
        ("negative patch", "1.2.-3"),
        ("leading zero major", "01.2.3"),
        ("leading zero minor", "1.02.3"),
        ("leading zero patch", "1.2.03"),
        ("empty major", ".2.3"),
        ("empty minor", "1..3"),
        ("empty patch", "1.2."),
        ("too many dots", "1.2.3.4"),
        ("prerelease empty", "1.2.3-"),
        ("prerelease empty first identifier", "1.2.3-.abc"),
        ("prerelease empty identifier", "1.2.3-1..2"),
        ("prerelease numeric leading 0", "1.2.3-01"),
        ("prerelease bad character", "1.2.3-/"),
        ("prerelease underscore", "1.2.3-abc_edf"),
        ("build empty", "1.2.3+"),
        ("build empty identifier", "1.2.3+1..2"),
        ("multiple build", "1.2.3+1.2+abc"),
        ("build bad character", "1.2.3+/"),
        ("build underscore", "1.2.3+abc_edf"),
        ("only prerelease", "-abc"),
        ("only build", "+abc"),
        ("only prerelease and build", "-abc+edf"),
        ("only text", "abc"),
        ("only identifier", "abc.edf"),
        ("minor snapshot", "1.2-SNAPSHOT"),
        ("dot dev", "1.2.3.DEV"),
    ],
)
def test_parse__invalid_version_text__error(version_text: str, description: str):
    with pytest.raises(ValueError):
        Version.parse(version_text)


@pytest.mark.parametrize(
    ["description", "kwargs"],
    [
        (
            "negative major",
            {
                "major": -1,
                "minor": 2,
                "patch": 3,
            },
        ),
        (
            "negative minor",
            {
                "major": 1,
                "minor": -2,
                "patch": 3,
            },
        ),
        (
            "negative patch",
            {
                "major": 1,
                "minor": 2,
                "patch": -3,
            },
        ),
        (
            "prerelease empty identifier",
            {"major": 1, "minor": 2, "patch": 3, "prerelease": ("1", "", "2")},
        ),
        (
            "prerelease numeric leading 0",
            {"major": 1, "minor": 2, "patch": 3, "prerelease": ("01",)},
        ),
        (
            "prerelease bad character",
            {"major": 1, "minor": 2, "patch": 3, "prerelease": ("/",)},
        ),
        (
            "build empty identifier",
            {"major": 1, "minor": 2, "patch": 3, "build": ("1", "", "2")},
        ),
        ("build bad character", {"major": 1, "minor": 2, "patch": 3, "build": ("/",)}),
    ],
)
def test_init__invalid_version_text__error(kwargs, description: str):
    with pytest.raises(ValueError):
        Version(**kwargs)


@pytest.mark.parametrize(
    ["version_text", "expected_value"],
    [
        ("1.2.3", Version(1, 2, 3)),
        ("0.0.1", Version(0, 0, 1)),
        ("1.2.3-123", Version(1, 2, 3, prerelease=("123",))),
        ("1.2.3-SNAPSHOT-1", Version(1, 2, 3, prerelease=("SNAPSHOT-1",))),
        ("1.2.3-abc.edf", Version(1, 2, 3, prerelease=("abc", "edf"))),
        ("1.2.3+123", Version(1, 2, 3, build=("123",))),
        ("1.2.3+abc.edf", Version(1, 2, 3, build=("abc", "edf"))),
        ("1.2.3+build.123", Version(1, 2, 3, build=("build", "123"))),
        (
            "1.2.3-abc.edf+xyz.098",
            Version(1, 2, 3, prerelease=("abc", "edf"), build=("xyz", "098")),
        ),
        (
            "1.2.3+abc.edf-xyz.098",
            Version(1, 2, 3, build=("abc", "edf-xyz", "098")),
        ),
    ],
)
def test_parse__valid_version_text__expected_value(
    version_text: str, expected_value: Version
):
    assert Version.parse(version_text) == expected_value


@pytest.mark.parametrize(
    "version_text",
    [
        "1.2.3",
        "0.0.1",
        "1.2.3-123",
        "1.2.3-SNAPSHOT-1",
        "1.2.3-abc.edf",
        "1.2.3+123",
        "1.2.3+abc.edf",
        "1.2.3+build.123",
        "1.2.3-abc.edf+xyz.098",
        "1.2.3+abc.edf-xyz.098",
    ],
)
def test_str__same_as_parsed_text(version_text: str):
    version = Version.parse(version_text)
    assert str(version) == version_text


def test_next_major__all_after_major_dropped():
    initial_version = Version(
        sd.SOME_MAJOR,
        sd.SOME_MINOR,
        sd.SOME_PATCH,
        sd.SOME_PRERELEASE_PARTS,
        sd.SOME_BUILD_PARTS,
    )

    result = initial_version.next_major()

    assert result == Version(sd.SOME_MAJOR + 1, 0, 0)


def test_next_minor__all_after_minor_dropped():
    initial_version = Version(
        sd.SOME_MAJOR,
        sd.SOME_MINOR,
        sd.SOME_PATCH,
        sd.SOME_PRERELEASE_PARTS,
        sd.SOME_BUILD_PARTS,
    )

    result = initial_version.next_minor()

    assert result == Version(sd.SOME_MAJOR, sd.SOME_MINOR + 1, 0)


def test_next_patch__all_after_patch_dropped():
    initial_version = Version(
        sd.SOME_MAJOR,
        sd.SOME_MINOR,
        sd.SOME_PATCH,
        sd.SOME_PRERELEASE_PARTS,
        sd.SOME_BUILD_PARTS,
    )

    result = initial_version.next_patch()

    assert result == Version(sd.SOME_MAJOR, sd.SOME_MINOR, sd.SOME_PATCH + 1)


@pytest.mark.parametrize(
    ["left_hand", "right_hand", "expected_value"],
    [
        ("1.2.3", "1.2.3", False),
        ("0.2.3", "1.2.3", True),
        ("0.0.3", "0.2.3", True),
        ("0.0.1", "0.0.3", True),
        ("0.9.0", "0.10.0", True),
        ("0.9.999", "0.10.0", True),
        ("9.0.0", "10.0.0", True),
        ("9.9.0", "10.0.0", True),
        ("9.99999.0", "10.0.0", True),
        ("1.2.3-abc", "1.2.3", True),
        ("1.2.3-abc.edf", "1.2.3", True),
        ("1.2.3-abc", "1.2.3-bcd", True),
        ("1.2.3-ABC", "1.2.3-abc", True),
        ("1.2.3-1", "1.2.3-2", True),
        ("1.2.3-99", "1.2.3-abc", True),
        ("1.2.3-abc", "1.2.3-99", False),
        ("1.2.3-1", "1.2.3-1.2", True),
        ("1.2.3-abc", "1.2.3-abc.edf", True),
        ("1.2.3-abc.edf", "1.2.3+abc.edf", True),
    ],
)
def test_lt__expected_value(left_hand: str, right_hand: str, expected_value: bool):
    assert (Version.parse(left_hand) < Version.parse(right_hand)) == expected_value


@pytest.mark.parametrize("value", [_Numeric(1), _Alpha("abc"), Version(1, 2, 3)])
def test_lt__other_type__not_implemented(value):
    with pytest.raises(TypeError):
        _ = value < 1
