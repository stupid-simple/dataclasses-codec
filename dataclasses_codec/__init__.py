from typing import Any, Type, TypeVar
from .core import Codec
from .codecs.json import JSONCodec, json_field, JSON_MISSING, json_codec, JSONSerializable, JSONDeserializable

_T = TypeVar("_T")


def encode(obj: Any, codec: Codec = json_codec, **kwargs: Any) -> Any:
    """Encode a dataclass using the specified codec.
    
    By default, the JSON codec is used. See: `dataclasses_codec.codecs.json` for more details.
    
    """
    return codec.encode(obj, **kwargs)

def decode(cls: Type[_T], data: Any, codec: Codec = json_codec, **kwargs: Any) -> _T:
    """Decode data to a dataclass using the specified codec."""
    return codec.decode(cls, data, **kwargs)

def to_dict(obj: Any, *, to_camel_case: bool = False, **kwargs: Any) -> str:
    """Convert dataclass to dictionary.
    
    By default, the JSON codec is used. See: `dataclasses_codec.codecs.json` for more details.

    Args:
        obj: The dataclass instance to serialize.
        to_camel_case: Whether to convert the field names from snake_case to camelCase.
        kwargs: Additional keyword arguments to pass to the `JSONCodec.to_json` method.
    """
    return json_codec.to_dict(obj, to_camel_case=to_camel_case, **kwargs)

def from_dict(cls: Type[_T], data: Any, *, to_snake_case: bool = False, **kwargs: Any) -> _T:
    """Convert dictionary to dataclass.
    
    By default, the JSON codec is used. See: `dataclasses_codec.codecs.json` for more details.

    Args:
        cls: The dataclass type to deserialize to.
        data: The dictionary to deserialize.
        to_snake_case: Whether to convert the field names from camelCase to snake_case.
        kwargs: Additional keyword arguments to pass to the `JSONCodec.from_dict` method.
    """
    return json_codec.from_dict(cls, data, to_snake_case=to_snake_case, **kwargs)

def to_json(obj: Any, *, to_camel_case: bool = False, **kwargs: Any) -> str:
    """Convert dataclass to JSON string.
    
    By default, the JSON codec is used. See: `dataclasses_codec.codecs.json` for more details.

    Args:
        obj: The dataclass instance to serialize.
        to_camel_case: Whether to convert the field names from snake_case to camelCase.
        kwargs: Additional keyword arguments to pass to the `JSONCodec.to_json` method.
    """
    return json_codec.to_json(obj, to_camel_case=to_camel_case, **kwargs)

def from_json(cls: Type[_T], json_str: str, *, to_snake_case: bool = False, **kwargs: Any) -> _T:
    """Convert JSON string to dataclass.
    
    By default, the JSON codec is used. See: `dataclasses_codec.codecs.json` for more details.

    Args:
        cls: The dataclass type to deserialize to.
        json_str: The JSON string to deserialize.
        to_snake_case: Whether to convert the field names from camelCase to snake_case.
        kwargs: Additional keyword arguments to pass to the `JSONCodec.from_json` method.
    """
    return json_codec.from_json(cls, json_str, to_snake_case=to_snake_case, **kwargs)

__all__ = [
    'Codec', 'JSONCodec', 'JSONSerializable', 'JSONDeserializable',
    'json_field', 'JSON_MISSING',
    'encode', 'decode', 'to_dict', 'from_dict', 'to_json', 'from_json',
    'json_codec',
]
