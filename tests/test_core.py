import unittest
from dataclasses import dataclass
from dataclasses_codec import Codec
from typing import Any, Type, TypeVar

_T = TypeVar("_T")


class TestCodec(Codec):
    
    def encode(self, obj: Any, **kwargs: Any) -> Any:
        return obj
    
    def decode(self, cls: Type[_T], data: Any, **kwargs: Any) -> _T:
        return cls(**data)


class TestCodecInterface(unittest.TestCase):
    
    def test_codec_is_abstract(self):
        with self.assertRaises(TypeError):
            Codec()
    
    def test_codec_implementation(self):
        codec = TestCodec()
        
        result = codec.encode("test")
        self.assertEqual(result, "test")
        
        @dataclass
        class TestClass:
            value: str
        
        instance = codec.decode(TestClass, {"value": "test"})
        self.assertIsInstance(instance, TestClass)
        self.assertEqual(instance.value, "test")
    
    def test_codec_with_kwargs(self):
        codec = TestCodec()
        
        result = codec.encode("test", extra_param="value")
        self.assertEqual(result, "test")
        
        @dataclass
        class TestClass:
            value: str
        
        instance = codec.decode(TestClass, {"value": "test"}, extra_param="value")
        self.assertIsInstance(instance, TestClass)
        self.assertEqual(instance.value, "test")


