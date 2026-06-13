import pytest
from app.services.images import PollinationsGenerator, ImageGenerator


def test_image_generator_is_abstract():
    """Test that ImageGenerator cannot be instantiated."""
    with pytest.raises(TypeError):
        ImageGenerator()


def test_pollinations_generator_instantiation():
    """Test that PollinationsGenerator can be instantiated."""
    gen = PollinationsGenerator(timeout=30)
    assert gen.timeout == 30
    assert gen.base_url == "https://image.pollinations.ai"


def test_pollinations_generator_is_subclass():
    """Test that PollinationsGenerator implements ImageGenerator."""
    assert issubclass(PollinationsGenerator, ImageGenerator)
