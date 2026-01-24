# StupidSimple Dataclasses Codec

[![PyPI version](https://img.shields.io/pypi/v/dataclasses-codec.svg)](https://pypi.org/project/dataclasses-codec/)
[![Python versions](https://img.shields.io/pypi/pyversions/dataclasses-codec.svg)](https://pypi.org/project/dataclasses-codec/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/stupid-simple/dataclasses-codec/actions/workflows/test.yml/badge.svg)](https://github.com/stupid-simple/dataclasses-codec/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/stupid-simple/dataclasses-codec/branch/main/graph/badge.svg)](https://codecov.io/gh/stupid-simple/dataclasses-codec)

This native Python package allows to easily convert dataclasses into and from a serialized form. By default supports json.

## Installation

```bash
pip install dataclasses-codec
```

## Usage

The package provides functions to easily convert dataclasses into and from a serialized form. It uses by default the `json_codec` instance the package provides.

```python
from dataclasses import dataclass
from dataclasses_codec import encode, decode, to_json, from_json

@dataclass
class MyDataclass:
    first_name: str
    last_name: str

obj = MyDataclass("John", "Doe")

# Serializable Python dictionary. JSON by default.
encoded = encode(obj)
print(encoded)
# Output: {"first_name": "John", "last_name": 'Doe'}

decoded = decode(MyDataclass, encoded)
print(decoded)
# Output: MyDataclass(first_name="John", last_name="Doe")

# Native JSON handling

raw_json = to_json(obj)
print(raw_json)
# Output: '{"first_name": "John", "last_name": "Doe"}'

restored = from_json(MyDataclass, raw_json)
print(restored)
# Output: MyDataclass(first_name="John", last_name="Doe")
```

### JSON codec

The JSON codec is a first class citizen of the package. It allows to easily convert dataclasses into and from JSON strings.

Serialization can be customized by using the `json_field` value. It supports native conversion of:
- Types already supported by the native `json` module.
- `date`
- `datetime`
- `timedelta`
- `Decimal`
- `UUID`
- `Path`

Dataclasses can be nested to form complex objects. It supports `list`, `tuple`, `dict` and `Union` types.

`json_field` extends the native dataclass `field` decorator to support custom serialization and deserialization.

```python
from dataclasses import dataclass
from dataclasses_codec import json_codec, JSONOptional, JSON_MISSING
from dataclasses_codec.codecs.json import json_field
import datetime as dt

# Still a dataclass, so we can use its features like slots, frozen, etc.
@dataclass(slots=True)
class MyMetadataDataclass:
    created_at: dt.datetime = field( # Dataclasses fields can be used as usual
        default_factory=lambda: dt.datetime.now()
    )
    updated_at: dt.datetime = json_field( # Json field also supports dataclasses field features.
        default_factory=lambda: dt.datetime.now(),
        serializer=lambda d: d.isoformat(), # Custom serializer to isoformat
        deserializer=lambda s: dt.datetime.fromisoformat(s)
    )
    enabled: bool | JSONOptional = JSON_MISSING # Explicitly mark a field as optional
    description: str | None = None # None is intentionally serialized as null


@dataclass
class MyDataclass:
    first_name: str
    last_name: str
    age: int
    metadata: MyMetadataDataclass = json_field(
        json_name="meta"
    )

obj = MyDataclass("John", "Doe", 30, MyMetadataDataclass(dt.datetime.now(), dt.datetime.now()))

raw_json = json_codec.to_json(obj)
print(raw_json)
# Output: '{"first_name": "John", "last_name": "Doe", "age": 30, "meta": {"created_at": "2025-10-25T11:53:35.918899", "updated_at": "2025-10-25T11:53:35.918902", "description": null}}'
```

### JSON Mixins

The package provides JSON mixins to add the serialization and deserialization capabilities to a dataclass.

By default, the JSON codec is used. See: `dataclasses_codec.codecs.json` for more details.

```python
from dataclasses import dataclass
from dataclasses_codec import JSONSerializable, JSONDeserializable

@dataclass
class MyDataclass(JSONSerializable, JSONDeserializable):
    first_name: str
    last_name: str
    age: int

obj = MyDataclass("John", "Doe", 30)

encoded = obj.to_dict(to_camel_case=True)
print(encoded)
# Output: {'firstName': 'John', 'lastName': 'Doe', 'age': 30}

restored = MyDataclass.from_dict(encoded, to_snake_case=True)
print(restored)
# Output: MyDataclass(first_name="John", last_name="Doe", age=30)
```

### Extensibility

The package allows to extend the functionality of the codecs by implementing the `Codec` interface.

Each implementation should use `is_dataclass` to check if the object is a dataclass.

```python
from dataclasses import dataclass, is_dataclass
from dataclasses_codec import Codec, encode
from dataclasses_codec.errors import CodecError

class MyCodec(Codec):
    def encode(self, obj, **kwargs):
        if not is_dataclass(obj):
            raise CodecError(f"obj is not a dataclass, found: '{obj}'")
        return obj
    def decode(self, cls, data, **kwargs):
        # Implement the decoding logic here
        raise CodecError("Decoding is not implemented for this codec")

@dataclass
class MyDataclass:
    first_name: str
    last_name: str
    age: int

obj = MyDataclass("John", "Doe", 30)

encoded = encode(obj, codec=MyCodec())
print(encoded)
# Output: {'first_name': 'John', 'last_name': 'Doe', 'age': 30}
```

## Development

### Running the tests

```bash
python -m unittest
```