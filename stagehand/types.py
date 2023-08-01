import re
import typing

import pydantic
import pydantic_core


Name = pydantic.constr(
    min_length=1,
    max_length=63,
    strip_whitespace=False,
    strict=True,
    pattern=r"^[a-z0-9A-Z\.\-_:]+$",
)


AnnotationName = pydantic.constr(
    strict=True, max_length=63, min_length=1, pattern=r"[A-Za-z0-9\-\./]+"
)
AnnotationValue = str
AnnotationDict = typing.Dict[AnnotationName, AnnotationValue]


LabelValue = pydantic.constr(
    strict=True, strip_whitespace=False, pattern=r"^[a-z0-9A-Z\.\-_:]{1,63}$"
)


class LabelName(pydantic.BaseModel):
    prefix: str | None = None
    name: str

    _label_key: typing.ClassVar[re.Pattern] = re.compile(
        r"^(?:(?P<prefix>(?:(?!-)[A-Za-z0-9\-]{1,253}(?<!-)\.)+(?:[A-Za-z]{2,6}))/)?(?P<name>[a-zA-Z\-\.]{1,63})$"
    )

    @classmethod
    def parse_label(cls, v: str) -> dict:
        if isinstance(v, dict):
            return v

        match = cls._label_key.match(v)
        if match is None:
            return None

        return match.groupdict()

    @classmethod
    def format(cls, prefix, name) -> str:
        return f"{prefix + '/' if prefix else ''}{name}"

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: typing.Any, handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.CoreSchema:
        return pydantic_core.core_schema.no_info_before_validator_function(
            function=cls.parse_label, schema=handler(cls)
        )

    def __str__(self) -> str:
        return self.format(self.prefix, self.name)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, __value: object) -> bool:
        return __value == str(self)


LabelDict = typing.Dict[LabelName, LabelValue]


class EntityReference(pydantic.BaseModel):
    name: Name
    kind: Name | None = None
    namespace: Name | None = None

    _entity_reference: typing.ClassVar[re.Pattern] = re.compile(
        r"^(?:(?P<kind>[a-zA-Z]{1,63}):)?(?:(?P<namespace>[a-zA-Z\-]{1,63})/)?(?P<name>[a-zA-Z\-0-9]{1,63})$"
    )

    @classmethod
    def validate_entity_reference(cls, v: str) -> dict:
        if isinstance(v, dict):
            return v

        default = {"name": None, "namespace": None, "kind": None}

        match = cls._entity_reference.match(v)
        if match is None:
            return default

        return match.groupdict()

    @classmethod
    def format(cls, kind: str | None, namespace: str | None, name: str) -> str:
        return (
            f"{kind + ':' if kind else ''}{namespace + '/' if namespace else ''}{name}"
        )

    @classmethod
    def parse(cls, s: str) -> "EntityReference":
        """Parses a string into an EntityReference class"""
        return cls(**cls.validate_entity_reference(s))

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        __source: type[pydantic.BaseModel],
        __handler: pydantic.GetCoreSchemaHandler,
    ) -> pydantic_core.CoreSchema:
        return pydantic_core.core_schema.no_info_before_validator_function(
            function=cls.validate_entity_reference, schema=__handler(cls)
        )

    def __str__(self) -> str:
        """Get the string representation of the reference"""
        return self.format(self.kind, self.namespace, self.name).lower()

    def __eq__(self, __value: object) -> bool:
        return __value == str(self)


TagValue = pydantic.constr(
    strict=True,
    strip_whitespace=False,
    min_length=1,
    max_length=63,
    pattern=r"^(?:(?:[a-z0-9:+#]+)-?)+$",
)
TagList = typing.List[TagValue]
