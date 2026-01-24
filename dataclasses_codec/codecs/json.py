"""
JSON codec implementation for dataclasses.
"""

import datetime as dt
import json
from typing import (
    Any, Type, TypeVar, Dict, Mapping, Callable, List,
    cast, Optional, get_origin, get_args, Union, final
)
from dataclasses import MISSING, Field, field, fields, is_dataclass
from types import NoneType, UnionType
from decimal import Decimal
from uuid import UUID
from pathlib import Path
from ..core import Codec
from ..errors import CodecError

_T = TypeVar("_T")

JSON_FIELD_NAME = "json_name"
JSON_SERIALIZER = "json_serializer"
JSON_DESERIALIZER = "json_deserializer"


class JSONCodec(Codec):
    """JSON serialization codec for dataclasses."""
    
    def __init__(self, to_camel_case: bool = False):
        self.to_camel_case = to_camel_case

    def encode(self, obj: Any, *, to_camel_case: bool = False, **_: Any) -> Any:
        return self.to_json(obj, to_camel_case=to_camel_case)
    
    def decode(self, cls: Type[_T], data: Any, *, to_snake_case: bool = False, **_: Any) -> _T:
        return self.from_json(cls, data, to_snake_case=to_snake_case)
    
    def to_dict(self, obj: Any, *, to_camel_case: bool = False, **_: Any) -> Any:
        """Encode dataclass to JSON-serializable dictionary.
        
        Args:
            obj: The dataclass instance to encode.
            to_camel_case: Whether to convert the field names from snake_case to camelCase.
        """
        if not is_dataclass(obj):
            raise CodecError(f"obj is not a dataclass, found: '{obj}'")
        try:
            return _encode(obj, to_camel_case= self.to_camel_case or to_camel_case)
        except Exception as e:
            raise CodecError(f"Error encoding object: {e}") from e
    
    def from_dict(self, cls: Type[_T], data: Any, *, to_snake_case: bool = False, **_: Any) -> _T:
        """Decode JSON-serializable dictionary data to dataclass.
        
        Args:
            cls: The dataclass type to decode to.
            data: The dictionary data to decode.
            to_snake_case: Whether to convert the field names from camelCase to snake_case.
        """
        if not is_dataclass(cls):
            raise CodecError(f"cls is not a dataclass, found: '{cls}'")
        try:
            return _decode_dataclass(cls, data, to_snake_case=self.to_camel_case or to_snake_case)
        except Exception as e:
            raise CodecError(f"Error decoding data: {e}") from e
    
    def to_json(self, obj: Any, *, to_camel_case: bool = False, **dump_kwargs: Any) -> str:
        """Serialize dataclass to JSON string.
        
        Args:
            obj: The dataclass instance to serialize.
            to_camel_case: Whether to convert the field names from snake_case to camelCase.
            dump_kwargs: Additional keyword arguments to pass to `json.dumps`.
        """
        try:
            return json.dumps(self.to_dict(obj, to_camel_case=to_camel_case), **dump_kwargs)
        except Exception as e:
            raise CodecError(f"Error serializing object: {e}") from e
    
    def from_json(self, cls: Type[_T], json_str: str, *, to_snake_case: bool = False, **load_kwargs: Any) -> _T:
        """Deserialize JSON string to dataclass.
        
        Args:
            cls: The dataclass type to deserialize to.
            json_str: The JSON string to deserialize.
            to_snake_case: Whether to convert the field names from camelCase to snake_case.
            load_kwargs: Additional keyword arguments to pass to `json.loads`.
        """
        try:
            data = json.loads(json_str, **load_kwargs)
            return self.from_dict(cls, data, to_snake_case=to_snake_case) 
        except Exception as e:
            raise CodecError(f"Error deserializing JSON: {e}") from e

json_codec = JSONCodec()


class JSONSerializable:
    """Mixin for serializable dataclasses.
    
    By default, the JSON codec is used. See: `dataclasses_codec.codecs.json` for more details.
    """
    
    def to_dict(self, *, codec: JSONCodec | None = None, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary using specified codec."""
        if codec is None:
            codec = json_codec
        return codec.to_dict(self, **kwargs)
    
    def to_json(self, *, codec: JSONCodec | None = None, **kwargs: Any) -> str:
        """Convert to JSON string using specified codec."""
        if codec is None:
            codec = json_codec
        return codec.to_json(self, **kwargs)

class JSONDeserializable:
    """Mixin for deserializable dataclasses.
    
    By default, the JSON codec is used. See: `dataclasses_codec.codecs.json` for more details.
    """
    
    @classmethod
    def from_dict(cls: Type[_T], data: Mapping[str, Any], *, codec: JSONCodec | None = None, **kwargs: Any) -> _T:
        """Create from dictionary using specified codec."""
        if codec is None:
            codec = json_codec
        return codec.from_dict(cls, data, **kwargs)
    
    @classmethod
    def from_json(cls: Type[_T], json_str: str, *, codec: JSONCodec | None = None, **kwargs: Any) -> _T:
        """Create from JSON string using specified codec."""
        if codec is None:
            codec = json_codec
        return codec.from_json(cls, json_str, **kwargs)



def snake_to_camel(s: str) -> str:
    """Convert snake_case string to camelCase."""
    return ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(s.split('_')))


def json_field(
    *,
    json_name: str | None = None,
    serializer: Callable[[Any], Any] | None = None,
    deserializer: Callable[[Any], Any] | None = None,
    **kwargs: Any,
) -> Any:
    """Create a dataclass field with custom JSON handling.
    
    Args:
        json_name: The name of the field in the JSON output. Ignores `to_camel_case` if provided.
        serializer: A callable to serialize the field value. If provided, overrides the default serializer.
        deserializer: A callable to deserialize the field value. If provided, overrides the default deserializer.
        kwargs: Additional keyword arguments to pass to the field.
    """
    metadata = kwargs.pop("metadata", {})
    if json_name is not None:
        metadata[JSON_FIELD_NAME] = json_name
    if serializer is not None:
        metadata[JSON_SERIALIZER] = serializer
    if deserializer is not None:
        metadata[JSON_DESERIALIZER] = deserializer
    return field(metadata=metadata, **kwargs)


@final
class JSONOptional:
    """Special value to indicate missing fields in JSON serialization."""
    def __bool__(self):
        return False


JSON_MISSING = JSONOptional()


def _get_json_field_name(
    field_obj: Optional[Field[Any]], field_name: str, to_camel_case: bool
) -> str:
    """Get the JSON field name, considering custom naming and camel case conversion."""
    if (
        field_obj
        and field_obj.metadata
        and JSON_FIELD_NAME in field_obj.metadata
    ):
        return field_obj.metadata[JSON_FIELD_NAME]

    if to_camel_case:
        return snake_to_camel(field_name)
    return field_name


def _encode(obj: Any, *_: Any, to_camel_case: bool) -> Any:
    if is_dataclass(obj):
        result: Dict[str, Any] = {}
        for field_ in fields(obj):
            value = getattr(obj, field_.name)
            if value is not JSON_MISSING:
                json_field_name = _get_json_field_name(
                    field_, field_.name, to_camel_case
                )
                if (
                    field_.metadata
                    and JSON_SERIALIZER in field_.metadata
                    and value is not None
                ):
                    value = field_.metadata[JSON_SERIALIZER](value)
                result[json_field_name] = _encode(
                    value, to_camel_case=to_camel_case
                )
        return result

    if isinstance(obj, dt.date):
        return obj.isoformat()

    if isinstance(obj, dt.datetime):
        return obj.isoformat()
    
    if isinstance(obj, dt.timedelta):
        return obj.total_seconds()
    
    if isinstance(obj, Decimal):
        return str(obj)
    
    if isinstance(obj, UUID):
        return str(obj)

    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, (list, tuple)):
        return [
            _encode(item, to_camel_case=to_camel_case)
            for item in cast(List[Any], obj)
        ]

    if isinstance(obj, dict):
        return {
            snake_to_camel(key)
            if to_camel_case and isinstance(key, str)
            else key: _encode(value, to_camel_case=to_camel_case)
            for key, value in obj.items()  # type: ignore
        }

    return obj


def _decode_dataclass(
    cls: Type[_T] | Any,
    raw: Mapping[str, Any],
    *_: Any,
    to_snake_case: bool = False,
) -> _T:
    if not is_dataclass(cls):
        raise ValueError(f"cls is not a dataclass, found: '{cls}'")

    kwargs: Dict[str, Any] = {}
    for field_ in fields(cls):
        json_name = _get_json_field_name(field_, field_.name, to_snake_case)

        if json_name not in raw:
            if field_.default is not MISSING:
                kwargs[field_.name] = field_.default
            elif field_.default_factory is not MISSING:
                kwargs[field_.name] = field_.default_factory()
            else:
                raise ValueError(f"missing field {json_name!r}")
            continue

        val = raw[json_name]
        if val is None:
            kwargs[field_.name] = None
            continue

        kwargs[field_.name] = _decode_field(
            field_.type, val, to_snake_case=to_snake_case, field_obj=field_
        )

    return cast(_T, cls(**kwargs))


def _decode_field(
    typ: Any,
    val: Any,
    *_: Any,
    to_snake_case: bool,
    field_obj: Field[Any] | None = None,
) -> Any:

    if (
        field_obj
        and field_obj.metadata
        and JSON_DESERIALIZER in field_obj.metadata
        and val is not None
    ):
        return field_obj.metadata[JSON_DESERIALIZER](val)

    if is_dataclass(typ):
        val = _decode_dataclass(typ, val, to_snake_case=to_snake_case)
    elif get_origin(typ) is tuple:
        val = tuple(
            _decode_field(get_args(typ)[i], v, to_snake_case=to_snake_case)
            for i, v in enumerate(val)
        )
    elif get_origin(typ) is list:
        inner = get_args(typ)[0]
        val = [
            _decode_field(inner, v, to_snake_case=to_snake_case) for v in val
        ]
    elif typ is dt.date:
        val = dt.date.fromisoformat(val)
    elif typ is dt.datetime:
        val = dt.datetime.fromisoformat(val)
    elif typ is Decimal:
        val = Decimal(val)
    elif typ is UUID:
        val = UUID(val)
    elif typ is Path:
        val = Path(val)
    elif typ is dt.timedelta:
        val = dt.timedelta(seconds=val)
    elif typ is NoneType:
        if val is not None:
            raise ValueError(f"expected None got: {val!r}")
    elif get_origin(typ) in (Union, UnionType):
        union_decoded = False
        for union_typ in get_args(typ):
            try:
                val = _decode_field(union_typ, val, to_snake_case=to_snake_case)
                union_decoded = True
                break
            except ValueError:
                ...
        if not union_decoded:
            raise ValueError(
                f"expected '{val!r}' to be of type '{typ!r}', got: {type(val)!r}"
            )
    elif val is None:
        raise ValueError(f"expected type {typ!r} got: None")
    return val


