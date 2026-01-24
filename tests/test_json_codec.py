"""
Tests for JSONCodec functionality.
"""

import unittest
import datetime as dt
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Union, Any, Dict
from dataclasses_codec import JSONCodec, json_field, JSON_MISSING
from dataclasses_codec.errors import CodecError
from uuid import UUID
from pathlib import Path


@dataclass
class SimpleClass:
    name: str
    age: int


@dataclass
class NestedClass:
    person: SimpleClass
    active: bool


@dataclass
class ClassWithDefaults:
    name: str
    age: int = 0
    email: str = ""


@dataclass
class ClassWithCustomFields:
    user_name: str = json_field(json_name="username")
    user_age: int = json_field(json_name="age")


@dataclass
class ClassWithSerializers:
    name: str
    date: dt.date = json_field(
        serializer=lambda d: d.isoformat(),
        deserializer=lambda s: dt.date.fromisoformat(s)
    )


@dataclass
class ClassWithOptional:
    name: str
    age: Optional[int] = None


@dataclass
class ClassWithList:
    name: str
    items: List[str]


class TestJSONCodec(unittest.TestCase):
    """Test JSONCodec functionality."""

    def setUp(self):
        self.codec = JSONCodec()
        self.camel_codec = JSONCodec(to_camel_case=True)

    def test_simple_encoding(self):
        obj = SimpleClass("Alice", 30)
        result = self.codec.to_dict(obj)
        expected = {"name": "Alice", "age": 30}
        self.assertEqual(result, expected)

    def test_simple_decoding(self):
        data = {"name": "Alice", "age": 30}
        result = self.codec.from_dict(SimpleClass, data)
        expected = SimpleClass("Alice", 30)
        self.assertEqual(result, expected)

    def test_nested_encoding(self):
        obj = NestedClass(SimpleClass("Alice", 30), True)
        result = self.codec.to_dict(obj)
        expected = {
            "person": {"name": "Alice", "age": 30},
            "active": True
        }
        self.assertEqual(result, expected)

    def test_nested_decoding(self):
        data = {
            "person": {"name": "Alice", "age": 30},
            "active": True
        }
        result = self.codec.from_dict(NestedClass, data)
        expected = NestedClass(SimpleClass("Alice", 30), True)
        self.assertEqual(result, expected)

    def test_camel_case_encoding(self):
        obj = SimpleClass("Alice", 30)
        result = self.camel_codec.to_dict(obj)
        expected = {"name": "Alice", "age": 30}  # No change for simple case
        self.assertEqual(result, expected)

    def test_camel_case_with_snake_case(self):
        @dataclass
        class SnakeCaseClass:
            user_name: str
            user_age: int

        obj = SnakeCaseClass("Alice", 30)
        result = self.camel_codec.to_dict(obj)
        expected = {"userName": "Alice", "userAge": 30}
        self.assertEqual(result, expected)

    def test_defaults_handling(self):
        obj = ClassWithDefaults("Alice")
        result = self.codec.to_dict(obj)
        expected = {"name": "Alice", "age": 0, "email": ""}
        self.assertEqual(result, expected)

    def test_defaults_decoding(self):
        data = {"name": "Alice"}
        result = self.codec.from_dict(ClassWithDefaults, data)
        expected = ClassWithDefaults("Alice", 0, "")
        self.assertEqual(result, expected)

    def test_custom_field_names(self):
        obj = ClassWithCustomFields("Alice", 30)
        result = self.codec.to_dict(obj)
        expected = {"username": "Alice", "age": 30}
        self.assertEqual(result, expected)

    def test_custom_field_names_decoding(self):
        data = {"username": "Alice", "age": 30}
        result = self.codec.from_dict(ClassWithCustomFields, data)
        expected = ClassWithCustomFields("Alice", 30)
        self.assertEqual(result, expected)

    def test_custom_serializers(self):
        obj = ClassWithSerializers("Alice", dt.date(2023, 1, 1))
        result = self.codec.to_dict(obj)
        expected = {"name": "Alice", "date": "2023-01-01"}
        self.assertEqual(result, expected)

    def test_custom_deserializers(self):
        data = {"name": "Alice", "date": "2023-01-01"}
        result = self.codec.from_dict(ClassWithSerializers, data)
        expected = ClassWithSerializers("Alice", dt.date(2023, 1, 1))
        self.assertEqual(result, expected)

    def test_optional_fields(self):
        obj = ClassWithOptional("Alice", None)
        result = self.codec.to_dict(obj)
        expected = {"name": "Alice", "age": None}
        self.assertEqual(result, expected)

    def test_optional_fields_decoding(self):
        data = {"name": "Alice", "age": None}
        result = self.codec.from_dict(ClassWithOptional, data)
        expected = ClassWithOptional("Alice", None)
        self.assertEqual(result, expected)

    def test_list_fields(self):
        obj = ClassWithList("Alice", ["item1", "item2"])
        result = self.codec.to_dict(obj)
        expected = {"name": "Alice", "items": ["item1", "item2"]}
        self.assertEqual(result, expected)

    def test_list_fields_decoding(self):
        data = {"name": "Alice", "items": ["item1", "item2"]}
        result = self.codec.from_dict(ClassWithList, data)
        expected = ClassWithList("Alice", ["item1", "item2"])
        self.assertEqual(result, expected)

    def test_to_json(self):
        obj = SimpleClass("Alice", 30)
        result = self.codec.to_json(obj)
        expected = '{"name": "Alice", "age": 30}'
        self.assertEqual(result, expected)

    def test_from_json(self):
        json_str = '{"name": "Alice", "age": 30}'
        result = self.codec.from_json(SimpleClass, json_str)
        expected = SimpleClass("Alice", 30)
        self.assertEqual(result, expected)

    def test_missing_required_field(self):
        data = {"name": "Alice"}  # Missing 'age'
        with self.assertRaises(CodecError) as context:
            self.codec.from_dict(SimpleClass, data)
        self.assertIn("missing field", str(context.exception))

    def test_invalid_dataclass(self):
        with self.assertRaises(CodecError) as context:
            self.codec.from_dict(str, {"test": "value"})
        self.assertIn("not a dataclass", str(context.exception))

    def test_json_missing_handling(self):
        @dataclass
        class ClassWithMissing:
            name: str
            optional_field: str = JSON_MISSING

        obj = ClassWithMissing("Alice")
        result = self.codec.to_dict(obj)
        expected = {"name": "Alice"}
        self.assertEqual(result, expected)


    def test_empty_dataclass(self):
        @dataclass
        class EmptyClass:
            pass

        obj = EmptyClass()
        result = self.codec.to_dict(obj)
        self.assertEqual(result, {})

        decoded = self.codec.from_dict(EmptyClass, {})
        self.assertEqual(decoded, EmptyClass())

    def test_datetime_handling(self):
        @dataclass
        class DateTimeClass:
            created_at: dt.datetime

        obj = DateTimeClass(dt.datetime(2023, 1, 1, 12, 0, 0))
        result = self.codec.to_dict(obj)
        expected = {"created_at": "2023-01-01T12:00:00"}
        self.assertEqual(result, expected)

        decoded = self.codec.from_dict(DateTimeClass, result)
        self.assertEqual(decoded, obj)

    def test_date_handling(self):
        @dataclass
        class DateClass:
            birth_date: dt.date

        obj = DateClass(dt.date(2023, 1, 1))
        result = self.codec.to_dict(obj)
        expected = {"birth_date": "2023-01-01"}
        self.assertEqual(result, expected)

        decoded = self.codec.from_dict(DateClass, result)
        self.assertEqual(decoded, obj)

    def test_union_types(self):
        @dataclass
        class UnionClass:
            value: Union[str, int]

        # Test with string
        obj1 = UnionClass("test")
        result1 = self.codec.to_dict(obj1)
        self.assertEqual(result1, {"value": "test"})

        decoded1 = self.codec.from_dict(UnionClass, result1)
        self.assertEqual(decoded1, obj1)

        # Test with int
        obj2 = UnionClass(42)
        result2 = self.codec.to_dict(obj2)
        self.assertEqual(result2, {"value": 42})

        decoded2 = self.codec.from_dict(UnionClass, result2)
        self.assertEqual(decoded2, obj2)

    def test_none_handling(self):
        @dataclass
        class NoneClass:
            value: Optional[str]

        obj = NoneClass(None)
        result = self.codec.to_dict(obj)
        expected = {"value": None}
        self.assertEqual(result, expected)

        decoded = self.codec.from_dict(NoneClass, result)
        self.assertEqual(decoded, obj)

    def test_unicode_strings(self):
        @dataclass
        class UnicodeClass:
            name: str
            description: str

        obj = UnicodeClass("测试", "这是一个测试")
        result = self.codec.to_dict(obj)
        expected = {"name": "测试", "description": "这是一个测试"}
        self.assertEqual(result, expected)

        decoded = self.codec.from_dict(UnicodeClass, result)
        self.assertEqual(decoded, obj)

    def test_special_characters(self):
        @dataclass
        class SpecialCharClass:
            text: str

        special_text = "Hello\nWorld\tTab\rCarriage\n\nMultiple"
        obj = SpecialCharClass(special_text)
        result = self.codec.to_dict(obj)
        expected = {"text": special_text}
        self.assertEqual(result, expected)

        decoded = self.codec.from_dict(SpecialCharClass, result)
        self.assertEqual(decoded, obj)

    def test_large_lists(self):
        @dataclass
        class LargeListClass:
            items: List[int]

        large_list = list(range(1000))
        obj = LargeListClass(large_list)

        result = self.codec.to_dict(obj)
        self.assertEqual(result["items"], large_list)

        decoded = self.codec.from_dict(LargeListClass, result)
        self.assertEqual(decoded.items, large_list)

    def test_very_deep_nesting(self):
        @dataclass
        class DeepNestedClass:
            level1: Dict[str, Any]

        # Create deeply nested structure
        obj = DeepNestedClass({
            "level2": {
                "level3": {
                    "level4": {
                        "level5": {
                            "value": "deep"
                        }
                    }
                }
            }
        })

        result = self.codec.to_dict(obj)
        self.assertEqual(result["level1"]["level2"]["level3"]["level4"]["level5"]["value"], "deep")

        decoded = self.codec.from_dict(DeepNestedClass, result)
        self.assertEqual(decoded.level1["level2"]["level3"]["level4"]["level5"]["value"], "deep")


    def test_decimal_roundtrip(self):
        """Decimal survives encode/decode roundtrip with full precision."""
        @dataclass
        class DecimalClass:
            amount: Decimal

        original = DecimalClass(Decimal("123.4567890123456789012345678901233455"))
        encoded = self.codec.to_json(original)
        decoded = self.codec.from_json(DecimalClass, encoded)
        self.assertEqual(decoded.amount, original.amount)

    def test_uuid_roundtrip(self):
        """UUID survives encode/decode roundtrip."""
        @dataclass
        class UUIDClass:
            id: UUID

        original = UUIDClass(UUID("123e4567-e89b-12d3-a456-426614174000"))
        encoded = self.codec.to_json(original)
        decoded = self.codec.from_json(UUIDClass, encoded)
        self.assertEqual(decoded.id, original.id)

    def test_path_roundtrip(self):
        """Path survives encode/decode roundtrip."""
        @dataclass
        class PathClass:
            path: Path

        original = PathClass(Path("test.txt"))
        encoded = self.codec.to_json(original)
        decoded = self.codec.from_json(PathClass, encoded)
        self.assertEqual(decoded.path, original.path)

    def test_timedelta_roundtrip(self):
        """Timedelta survives encode/decode roundtrip."""
        @dataclass
        class TimedeltaClass:
            duration: dt.timedelta

        original = TimedeltaClass(dt.timedelta(seconds=123456.124551))
        encoded = self.codec.to_json(original)
        decoded = self.codec.from_json(TimedeltaClass, encoded)
        self.assertEqual(decoded.duration, original.duration)