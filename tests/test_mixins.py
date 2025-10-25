"""
Tests for mixin classes.
"""

import unittest
from dataclasses import dataclass, field
from dataclasses_codec import (
    JSONSerializable, JSONDeserializable, 
    JSONCodec
)
from typing import Any, Type, TypeVar, List, Dict

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
class SerializableClass(JSONSerializable):
    name: str
    age: int


@dataclass
class DeserializableClass(JSONDeserializable):
    name: str
    age: int



class TestSerializable(unittest.TestCase):
    
    def test_to_dict_default_codec(self):
        obj = SerializableClass("Alice", 30)
        result = obj.to_dict()
        expected = {"name": "Alice", "age": 30}
        self.assertEqual(result, expected)
    
    def test_to_dict_custom_codec(self):
        obj = SerializableClass("Alice", 30)
        custom_codec = TestCodec()
        result = obj.to_dict(codec=custom_codec)
        expected = {"name": "test_Alice", "age": 30}
        self.assertEqual(result, expected)
    
    def test_to_json_default_codec(self):
        obj = SerializableClass("Alice", 30)
        result = obj.to_json()
        expected = '{"name": "Alice", "age": 30}'
        self.assertEqual(result, expected)
    
    def test_to_json_custom_codec(self):
        obj = SerializableClass("Alice", 30)
        custom_codec = TestCodec()
        result = obj.to_json(codec=custom_codec)
        expected = '{"name": "test_Alice", "age": 30}'
        self.assertEqual(result, expected)
    
    def test_to_json_with_kwargs(self):
        """Test to_json with additional kwargs."""
        obj = SerializableClass("Alice", 30)
        result = obj.to_json(separators=(',', ':'))
        expected = '{"name":"Alice","age":30}'
        self.assertEqual(result, expected)


class TestDeserializable(unittest.TestCase):
    
    def test_from_dict_default_codec(self):
        data = {"name": "Alice", "age": 30}
        result = DeserializableClass.from_dict(data)
        expected = DeserializableClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_from_dict_custom_codec(self):
        data = {"name": "test_Alice", "age": 30}
        custom_codec = TestCodec()
        result = DeserializableClass.from_dict(data, codec=custom_codec)
        expected = DeserializableClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_from_json_default_codec(self):
        json_str = '{"name": "Alice", "age": 30}'
        result = DeserializableClass.from_json(json_str)
        expected = DeserializableClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_from_json_custom_codec(self):
        json_str = '{"name": "test_Alice", "age": 30}'
        custom_codec = TestCodec()
        result = DeserializableClass.from_json(json_str, codec=custom_codec)
        expected = DeserializableClass("Alice", 30)
        self.assertEqual(result, expected)
    
    def test_from_json_with_kwargs(self):
        json_str = '{"name":"Alice","age":30}'
        result = DeserializableClass.from_json(json_str)
        expected = DeserializableClass("Alice", 30)
        self.assertEqual(result, expected)



class TestMixinInheritance(unittest.TestCase):
    
    def test_multiple_inheritance(self):
        @dataclass
        class CustomClass(JSONSerializable, JSONDeserializable):
            name: str
            age: int
        
        obj = CustomClass("Alice", 30)
        
        data = obj.to_dict()
        restored = CustomClass.from_dict(data)
        self.assertEqual(obj, restored)
    
    def test_mixin_with_other_classes(self):
        class BaseClass:
            def __init__(self, base_value: str):
                self.base_value = base_value
        
        @dataclass
        class MixedClass(BaseClass, JSONSerializable, JSONDeserializable):
            name: str
            age: int
            
            def __post_init__(self):
                super().__init__("base")
        
        obj = MixedClass("Alice", 30)
        
        data = obj.to_dict()
        expected = {"name": "Alice", "age": 30}
        self.assertEqual(data, expected)

        restored = MixedClass.from_dict(data)
        self.assertEqual(restored.name, "Alice")
        self.assertEqual(restored.age, 30)
    
    def test_empty_dataclass(self):
        @dataclass
        class EmptyClass(JSONSerializable, JSONDeserializable):
            pass
        
        obj = EmptyClass()
        result = obj.to_dict()
        self.assertEqual(result, {})
        
        restored = EmptyClass.from_dict({})
        self.assertEqual(restored, obj)
    
    def test_dataclass_with_only_defaults(self):
        @dataclass
        class DefaultsOnlyClass(JSONSerializable, JSONDeserializable):
            name: str = "default"
            age: int = 0
        
        obj = DefaultsOnlyClass()
        result = obj.to_dict()
        expected = {"name": "default", "age": 0}
        self.assertEqual(result, expected)
        
        restored = DefaultsOnlyClass.from_dict({})
        self.assertEqual(restored, obj)
    
    def test_dataclass_with_factory_defaults(self):
        @dataclass
        class FactoryDefaultsClass(JSONSerializable, JSONDeserializable):
            items: List[str] = field(default_factory=list)
            metadata: Dict[str, Any] = field(default_factory=dict)
        
        obj = FactoryDefaultsClass()
        result = obj.to_dict()
        expected = {"items": [], "metadata": {}}
        self.assertEqual(result, expected)
        
        restored = FactoryDefaultsClass.from_dict({})
        self.assertEqual(restored, obj)
    
    def test_nested_empty_structures(self):
        @dataclass
        class NestedEmptyClass(JSONSerializable, JSONDeserializable):
            items: List[Dict[str, Any]] = field(default_factory=list)
            metadata: Dict[str, List[str]] = field(default_factory=dict)
        
        obj = NestedEmptyClass()
        result = obj.to_dict()
        expected = {"items": [], "metadata": {}}
        self.assertEqual(result, expected)
        
        restored = NestedEmptyClass.from_dict({})
        self.assertEqual(restored, obj)
    
    def test_large_nested_structure(self):
        @dataclass
        class LargeNestedClass(JSONSerializable, JSONDeserializable):
            data: Dict[str, Any]
        
        large_data = {}
        for i in range(100):
            large_data[f"key_{i}"] = {
                "nested": {
                    "value": i,
                    "items": list(range(10))
                }
            }
        
        obj = LargeNestedClass(large_data)
        result = obj.to_dict()
        self.assertEqual(len(result["data"]), 100)
        
        restored = LargeNestedClass.from_dict(result)
        self.assertEqual(restored.data["key_0"]["nested"]["value"], 0)
        self.assertEqual(restored.data["key_99"]["nested"]["value"], 99)
    
    def test_memory_efficient_encoding(self):
        @dataclass
        class MemoryEfficientClass(JSONSerializable, JSONDeserializable):
            items: List[str]
        
        large_list = [f"item_{i}" for i in range(10000)]
        obj = MemoryEfficientClass(large_list)
        
        result = obj.to_dict()
        self.assertEqual(len(result["items"]), 10000)
        
        restored = MemoryEfficientClass.from_dict(result)
        self.assertEqual(restored.items, large_list)


