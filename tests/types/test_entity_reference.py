import pytest
import pydantic
from stagehand.types import EntityReference

from devtools import debug


def test_formatting():
    entity = EntityReference(
        kind="group", namespace="spam", name="developer-experience"
    )
    assert str(entity) == "group:spam/developer-experience"


def test_basic_parsing():
    class TestModel(pydantic.BaseModel):
        entity: EntityReference

    entity = EntityReference.parse("group:spam/developer-experience")
    TestModel.model_validate({"entity": "group:spam/developer-experience"})

    assert entity.name == "developer-experience"
    assert entity.namespace == "spam"
    assert entity.kind == "group"


@pytest.mark.parametrize("ref", ["group:asdf#", "group::asdf", "group//zzz", ":/name"])
def test_bad_characters(ref):
    with pytest.raises(pydantic.ValidationError):
        EntityReference.parse(ref)


@pytest.mark.parametrize(
    "kind,namespace,name",
    [
        ("group", "spam", "developer-experience"),
        (None, "spam", "developer-experience"),
        ("group", None, "developer-experience"),
        (None, None, "developer-experience"),
    ],
)
def test_entity_field_parsing(kind, namespace, name):
    entity = EntityReference(kind=kind, namespace=namespace, name=name)
    assert entity.name == name
    assert entity.namespace == namespace
    assert entity.kind == kind
