import pydantic

from . import types


class Relationship(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")
    type: str
    ref: types.EntityReference = pydantic.Field(alias="targetRef")
    target: types.EntityReference | None = None
    metadata: dict = {}


class Specification(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")
    owner: types.EntityReference | None = None
    type: str | None = None
    children: list[str] = []


class Link(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")
    url: pydantic.AnyUrl
    title: str


class Metadata(pydantic.BaseModel):
    name: types.Name
    uid: pydantic.UUID4 | None = None
    etag: str | None = None
    namespace: types.Name = "default"
    description: str | None = None
    annotations: types.AnnotationDict = {}
    labels: types.LabelDict = {}
    links: list[Link] = []
    tags: types.TagList = []


class Entity(pydantic.BaseModel):
    api_version: str = pydantic.Field(alias="apiVersion")
    kind: str
    metadata: Metadata
    spec: Specification
    relations: list[Relationship] = []

    @property
    def children(self) -> list[str]:
        return self.spec.children

    @property
    def annotations(self) -> types.AnnotationDict:
        return self.metadata.annotations

    @property
    def labels(self) -> types.LabelDict:
        return self.metadata.labels

    @property
    def tags(self) -> types.TagList:
        return self.metadata.tags

    @property
    def entity_reference(self) -> types.EntityReference:
        return types.EntityReference.format(
            self.kind, self.metadata.namespace, self.metadata.name
        )
