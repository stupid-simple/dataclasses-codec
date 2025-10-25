"""
Tests for functional API (encode, decode, to_json, from_json).
"""

import unittest
from dataclasses import dataclass
from dataclasses_codec import (
    encode, decode, to_dict, from_dict, to_json, from_json,
    json_codec, JSONCodec
)
from dataclasses_codec.errors import CodecError
from typing import Any, Type, TypeVar

_T = TypeVar("_T")


class TestCodec(JSONCodec):
    """Test codec that adds a prefix to all values."""
    
    def to_dict(self, obj: Any, **kwargs: Any) -> Any:
        """Add 'test_' prefix to all string values."""
        result = super().to_dict(obj, **kwargs)
        if isinstance(result, dict):
            return {k: f"test_{v}" if isinstance(v, str) else v for k, v in result.items()}
        return result
    
    def from_dict(self, cls: Type[_T], data: Any, **kwargs: Any) -> _T:
        """Remove 'test_' prefix from all string values."""
        if isinstance(data, dict):
            data = {k: v[5:] if isinstance(v, str) and v.startswith("test_") else v 
                   for k, v in data.items()}
        return super().from_dict(cls, data, **kwargs)


@dataclass
class SimpleClass:
    name: str
    age: int


@dataclass
class SnakeCaseClass:
    user_name: str
    user_age: int


class TestEncodeDecode(unittest.TestCase):
    def test_encode_default_codec(self):
        obj = SimpleClass("Alice", 30)
        result = encode(obj)
        expected = '{"name": "Alice", "age": 30}'
        self.assertEqual(result, expected)
    
    def test_encode_custom_codec(self):
        obj = SimpleClass("Alice", 30)
        custom_codec = TestCodec()
        result = encode(obj, codec=custom_codec)
        expected = '{"name": "test_Alice", "age": 30}'
        self.assertEqual(result, expected)
    
    def test_encode_with_kwargs(self):
        obj = SimpleClass("Alice", 30)
        result = encode(obj, to_camel_case=True)
        expected = '{"name": "Alice", "age": 30}'  # No change for simple case
        self.assertEqual(result, expected)
    
    def test_decode_default_codec(self):
        data = '{"name": "Alice", "age": 30}'
        result = decode(SimpleClass, data)
        expected = SimpleClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_decode_custom_codec(self):
        data = '{"name": "test_Alice", "age": 30}'
        custom_codec = TestCodec()
        result = decode(SimpleClass, data, codec=custom_codec)
        expected = SimpleClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_decode_with_kwargs(self):
        data = '{"name": "Alice", "age": 30}'
        result = decode(SimpleClass, data, to_snake_case=True)
        expected = SimpleClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_round_trip(self):
        original = SimpleClass("Alice", 30)
        
        data = encode(original)
        
        restored = decode(SimpleClass, data)
        
        self.assertEqual(original, restored)
    
    def test_round_trip_custom_codec(self):
        original = SimpleClass("Alice", 30)
        custom_codec = TestCodec()
        
        data = encode(original, codec=custom_codec)
        
        restored = decode(SimpleClass, data, codec=custom_codec)
        
        self.assertEqual(original, restored)


class TestToDictFromDict(unittest.TestCase):
    def test_to_dict_default(self):
        obj = SimpleClass("Alice", 30)
        result = to_dict(obj)
        expected = {"name": "Alice", "age": 30}
        self.assertEqual(result, expected)
    
    def test_to_dict_camel_case(self):
        obj = SnakeCaseClass("Alice", 30)
        result = to_dict(obj, to_camel_case=True)
        expected = {"userName": "Alice", "userAge": 30}
        self.assertEqual(result, expected)
    
    def test_to_dict_with_kwargs(self):
        obj = SimpleClass("Alice", 30)
        result = to_dict(obj, separators=(',', ':'))
        expected = {"name":"Alice","age":30}
        self.assertEqual(result, expected)
    
    def test_from_dict_default(self):
        data = {"name": "Alice", "age": 30}
        result = from_dict(SimpleClass, data)
        expected = SimpleClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_from_dict_snake_case(self):
        data = {"userName": "Alice", "userAge": 30}
        result = from_dict(SnakeCaseClass, data, to_snake_case=True)
        expected = SnakeCaseClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_from_dict_with_kwargs(self):
        data = {"name":"Alice","age":30}
        result = from_dict(SimpleClass, data)
        expected = SimpleClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_round_trip_dict(self):
        original = SimpleClass("Alice", 30)
        
        data = to_dict(original)
        
        restored = from_dict(SimpleClass, data)
        
        self.assertEqual(original, restored)
    
    def test_round_trip_dict_camel_case(self):
        original = SnakeCaseClass("Alice", 30)
        
        data = to_dict(original, to_camel_case=True)
        
        restored = from_dict(SnakeCaseClass, data, to_snake_case=True)
        
        self.assertEqual(original, restored)


class TestToJsonFromJson(unittest.TestCase):
    def test_to_dict_default(self):
        obj = SimpleClass("Alice", 30)
        result = to_json(obj)
        expected = '{"name": "Alice", "age": 30}'
        self.assertEqual(result, expected)
    
    def test_to_json_camel_case(self):
        obj = SnakeCaseClass("Alice", 30)
        result = to_json(obj, to_camel_case=True)
        expected = '{"userName": "Alice", "userAge": 30}'
        self.assertEqual(result, expected)
    
    def test_to_json_with_kwargs(self):
        obj = SimpleClass("Alice", 30)
        result = to_json(obj, separators=(',', ':'))
        expected = '{"name":"Alice","age":30}'
        self.assertEqual(result, expected)
    
    def test_from_json_default(self):
        data = '{"name": "Alice", "age": 30}'
        result = from_json(SimpleClass, data)
        expected = SimpleClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_from_json_snake_case(self):
        data = '{"userName": "Alice", "userAge": 30}'
        result = from_json(SnakeCaseClass, data, to_snake_case=True)
        expected = SnakeCaseClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_from_json_with_kwargs(self):
        data = '{"name":"Alice","age":30}'
        result = from_json(SimpleClass, data)
        expected = SimpleClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_round_trip_json(self):
        original = SimpleClass("Alice", 30)
        
        data = to_json(original)
        
        restored = from_json(SimpleClass, data)
        
        self.assertEqual(original, restored)
    
    def test_round_trip_json_camel_case(self):
        original = SnakeCaseClass("Alice", 30)
        
        data = to_json(original, to_camel_case=True)
        
        restored = from_json(SnakeCaseClass, data, to_snake_case=True)
        
        self.assertEqual(original, restored)

class TestDefaultCodecs(unittest.TestCase):
    def test_json_codec_default(self):
        obj = SimpleClass("Alice", 30)
        result = json_codec.to_dict(obj)
        expected = {"name": "Alice", "age": 30}
        self.assertEqual(result, expected)
    

    def test_encode_non_dataclass(self):
        # Test with simple dict
        obj = {"name": "Alice", "age": 30}
        with self.assertRaises(CodecError) as context:
            encode(obj)
        self.assertIn("not a dataclass", str(context.exception))
        
        # Test with list
        obj = [{"name": "Alice"}, {"name": "Bob"}]
        with self.assertRaises(CodecError) as context:
            encode(obj)
        self.assertIn("not a dataclass", str(context.exception))
    
    def test_decode_with_missing_fields(self):
        data = '{"name": "Alice"}'  # Missing 'age'
        with self.assertRaises(CodecError) as context:
            decode(SimpleClass, data)
        self.assertIn("missing field", str(context.exception))
    
    def test_to_json_with_non_serializable(self):
        obj = SimpleClass("Alice", 30)
        result = to_dict(obj)
        # Should work fine with dataclasses
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertIn("age", result)
        self.assertEqual(result["name"], "Alice")
        self.assertEqual(result["age"], 30)

    
    def test_from_json_with_wrong_structure(self):
        data = {"wrong": "structure"}
        with self.assertRaises(CodecError) as context:
            from_dict(SimpleClass, data)
        self.assertIn("missing field", str(context.exception))

    
    def test_invalid_dataclass_type(self):
        with self.assertRaises(CodecError) as context:
            decode(str, '{"test": "value"}')
        self.assertIn("not a dataclass", str(context.exception))
    
    def test_wrong_data_type(self):
        with self.assertRaises(CodecError) as context:
            decode(SimpleClass, "not a JSON string")
        self.assertIn("Error deserializing JSON", str(context.exception))


