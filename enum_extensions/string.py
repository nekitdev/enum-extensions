from enum_extensions.constants import COMMA_SPACE, EMPTY, PIPE, SPACE, TICK, UNDER

__all__ = ("case_fold", "case_fold_name", "concat_comma_space", "create_title", "tick")

concat_comma_space = COMMA_SPACE.join
concat_pipe = PIPE.join
tick = TICK.format

is_upper = str.isupper
is_lower = str.islower


def create_title(name: str) -> str:
    if is_upper(name) or is_lower(name):
        return name.replace(UNDER, SPACE).title()

    return name


case_fold = str.casefold


def case_fold_name(name: str) -> str:
    return case_fold(name.replace(UNDER, EMPTY))
