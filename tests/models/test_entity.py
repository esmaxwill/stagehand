import pytest
import pydantic
from stagehand.models import Entity

from devtools import debug

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


def test_parsing():
    entity = Entity.model_validate_json(doc)


def test_parsing():
    entity = Entity.model_validate_json(doc)
    assert "portal" in entity.tags
    assert "github.com/hello" in entity.labels
    assert entity.labels["github.com/hello"] == "world"
    assert entity.entity_reference == "system:default/artist-engagement-portal"
