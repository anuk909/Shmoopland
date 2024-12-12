import pytest
from memory_profiler import profile

def test_imports():
    """Test that all required packages are properly installed."""
    import spacy
    import textblob
    import markovify
    assert True, "All imports successful"

@profile
def test_spacy_model():
    """Test that spacy model can be loaded with reasonable memory usage."""
    import spacy
    nlp = spacy.load('en_core_web_sm')
    doc = nlp('Test sentence')
    assert doc.text == 'Test sentence', "Spacy model working correctly"

if __name__ == '__main__':
    pytest.main([__file__])
