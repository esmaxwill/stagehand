import pytest
import pydantic

from devtools import debug

from stagehand.types import TagList, TagValue

doc = """{
  "apiVersion": "backstage.io/v1alpha1",
  "kind": "System",
  "metadata": {
    "name": "artist-engagement-portal",
    "description": "Everything related to artists",
    "tags": [
      "portal"
    ],
    "labels": {
      "github.com/hello": "world"
    }
  },
  "spec": {
    "owner": "team-a",
    "domain": "artists"
  }
}"""


@pytest.mark.parametrize(
    "value",
    [
        "java",
        "go",
        "serverless",
        "serverless-lambda",
        "serverless-python-requirements",
        "serverless--lambda",
        "serverless-lambda#big-cupcakes",
        "serverless:lambda",
        "a" * 63,
    ],
)
def test_tag_values(value):
    adapter = pydantic.TypeAdapter(TagValue)
    debug(adapter.validate_python(value))


@pytest.mark.parametrize(
    "value",
    ["serverless--python", "a" * 64, "serverless!", f"{'a'*15}--{'b'*34}-{'c'*34}"],
)
def test_tag_values(value):
    adapter = pydantic.TypeAdapter(TagValue)
    with pytest.raises(pydantic.ValidationError):
        assert adapter.validate_python(value) == value
