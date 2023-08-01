import re


_label_value_default = {"prefix": None, "name": None}


_entity_reference = re.compile(
    r"^(?:(?P<kind>[a-zA-Z]{1,63}):)?(?:(?P<namespace>[a-zA-Z\-]{1,63})/)?(?P<name>[a-zA-Z\-0-9]{1,63})$"
)


def validate_entity_reference(v: str) -> dict:
    if isinstance(v, dict):
        return v

    default = {"name": None, "namespace": None, "kind": None}

    match = _entity_reference.match(v)
    if match is None:
        return default

    return match.groupdict()


_label_key = re.compile(
    r"^(?:(?P<prefix>(?:(?!-)[A-Za-z0-9\-]{1,253}(?<!-)\.)+(?:[A-Za-z]{2,6}))/)?(?P<name>[a-zA-Z\-\.]{1,63})$"
)


def parse_label(v: str) -> dict:
    if isinstance(v, dict):
        return v

    match = _label_key.match(v)
    if match is None:
        return None

    return match.groupdict()


# _label_value_regex = re.compile(r"^[a-z0-9A-Z\.\-_:]{1,63}$")
# def validate_label_value(v: str) -> str:
#     assert _label_value_regex.match(v), "Label value doesn't match documented pattern"
#     return v


def validate_tag_value(v: str) -> str:
    assert re.match(
        r"[a-z0-9:+#\-]{1,63}", v
    ), "Tag value doesn't match documented pattern"
    return v
