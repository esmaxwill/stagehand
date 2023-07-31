import pytest
import pydantic

from stagehand.types import LabelName, LabelValue, LabelDict

from devtools import debug


@pytest.mark.parametrize(
    "label",
    [
        "github.com/asdf",
        "app.kubernetes.io/managed-by",
        "app.kubernetes.io/instance",
        "config.kubernetes.io/local-config",
        "pagerduty.com/integration-key",
        "backstage.io/techdocs-ref",
    ],
)
def test_label_name(label):
    class TestModel(pydantic.BaseModel):
        label: LabelName

    TestModel.model_validate({"label": label})


def test_bad_label_name():
    class TestModel(pydantic.BaseModel):
        label: LabelName

    with pytest.raises(pydantic.ValidationError):
        TestModel.model_validate({"label": "argocd/app-name"})


def test_label_formatting():
    assert str(LabelName(prefix="github.com", name="asdf")) == "github.com/asdf"


def test_label_dict():
    good = {"labels": {"github.com/asdf": "asdf"}}
    bad = {"labels": {"argocd/app-name": "asdf"}}

    class TestModel(pydantic.BaseModel):
        labels: LabelDict

    TestModel.model_validate(good)

    with pytest.raises(pydantic.ValidationError):
        TestModel.model_validate(bad)
