from enum_extensions.string import case_fold_name, create_title

NAME = "NAME"
NAME_CASE_FOLD = "name"
NAME_TITLE = "Name"

SOME_NAME = "SOME_NAME"
SOME_NAME_CASE_FOLD = "somename"
SOME_NAME_TITLE = "Some Name"

OTHER_NAME = "other_name"
OTHER_NAME_CASE_FOLD = "othername"
OTHER_NAME_TITLE = "Other Name"

TITLE_NAME = "Title"
TITLE_NAME_CASE_FOLD = "title"
TITLE_NAME_TITLE = "Title"


def test_case_fold_name() -> None:
    assert case_fold_name(NAME) == NAME_CASE_FOLD
    assert case_fold_name(SOME_NAME) == SOME_NAME_CASE_FOLD
    assert case_fold_name(OTHER_NAME) == OTHER_NAME_CASE_FOLD
    assert case_fold_name(TITLE_NAME) == TITLE_NAME_CASE_FOLD


def test_create_title() -> None:
    assert create_title(NAME) == NAME_TITLE
    assert create_title(SOME_NAME) == SOME_NAME_TITLE
    assert create_title(OTHER_NAME) == OTHER_NAME_TITLE
    assert create_title(TITLE_NAME) == TITLE_NAME_TITLE
