import abc
import httpx
import itertools
import typing
import urllib.parse


from stagehand.types import EntityReference
from stagehand.models import Entity

from devtools import debug


class FilterBase(abc.ABC):
    @abc.abstractmethod
    def render(self) -> str:
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.render())


class Fields(FilterBase):
    def __init__(self, fields: str | list[str]) -> None:
        self.fields: list[str] = [fields] if isinstance(fields, str) else fields

    def render(self) -> str:
        return ",".join(
            itertools.chain(["apiVersion", "spec", "metadata"], self.fields)
        )


class Filter(FilterBase):
    def __init__(self, path: str) -> None:
        self.path: str = path
        self.value: str | int | None = None

    def equals(self, value: str) -> "Filter":
        self.value = value
        return self

    def exists(self) -> "Filter":
        self.value = None
        return self

    def __repr__(self) -> str:
        return f"Filter<{self.path}={self.value}>"

    def render(self) -> str:
        return f"{self.path}{'='+self.value if self.value else ''}"


class Owner(FilterBase):
    def __init__(self, reference: str, recursive: bool = True) -> None:
        self.reference: EntityReference = EntityReference.parse(reference)
        self.recursive = recursive

    def render(self) -> Filter:
        return Filter("relations.ownedBy").equals(str(self.reference))

    def __repr__(self) -> str:
        return f"Owner<{self.reference}>"


class Client:
    def __init__(self, backstage_url: str) -> None:
        self.backstage_url = backstage_url

    def _resolve_owners(self, filters: list[FilterBase]) -> str:
        for owner in [x for x in filters if isinstance(x, Owner)]:
            yield Owner(reference=str(owner.reference), recursive=False).render()

            if owner.recursive:
                owner_entity = self.entity(owner.reference)
                yield from [
                    Owner(reference=str(x), recursive=False).render()
                    for x in owner_entity.children
                ]

    def _render_filters(self, filters: list[FilterBase]) -> str:
        return ",".join([x.render() for x in filters if isinstance(x, Filter)])

    def _get_entities(self, params) -> typing.Generator[Entity, None, None]:
        session = httpx.Client()
        url = f"{self.backstage_url}/api/catalog/entities"

        while True:
            response = session.get(url, params=params)
            response.raise_for_status()

            yield from response.json()

            if not response.links:
                break

            next = urllib.parse.urlparse(response.links["next"]["url"])
            next_params = urllib.parse.parse_qs(next.query)
            params.update(next_params)

    def entity(self, reference: str | EntityReference) -> Entity:
        entity = (
            EntityReference.parse(reference)
            if isinstance(reference, str)
            else reference
        )

        response = httpx.get(
            f"{self.backstage_url}/api/catalog/entities/by-name/{entity.kind}/{entity.namespace or 'default'}/{entity.name}"
        )
        return Entity.model_validate(response.json())

    def entities(
        self,
        *filters,
        offset: int | None = None,
        limit: int | None = None,
        after: str | None = None,
        fields: Fields | None = None,
    ) -> typing.Generator[Entity, None, None]:
        params = {}

        filter_string = self._render_filters(
            itertools.chain(filters, self._resolve_owners(filters))
        )

        if filter_string:
            params["filter"] = filter_string

        if limit is not None:
            params["limit"] = limit

        if offset is not None:
            params["offset"] = offset

        if after is not None:
            params["after"] = after

        if fields is not None:
            params["fields"] = fields.render()

        for entity in self._get_entities(params):
            yield Entity.model_validate(entity)
