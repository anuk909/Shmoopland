import pytest
from memory_profiler import profile
import psutil

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

    # Test with multiple sentences to verify memory stability
    sentences = [
        "The crystal glows with mysterious energy.",
        "A merchant offers rare magical items.",
        "The ancient tower reaches toward the stars.",
        "Mysterious runes cover the ancient walls."
    ]

    initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

    for sentence in sentences:
        doc = nlp(sentence)
        assert doc.text == sentence

        # Analyze entities and dependencies
        entities = [ent.text for ent in doc.ents]
        deps = [token.dep_ for token in doc]

        # Memory shouldn't grow significantly
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        assert current_memory - initial_memory < 10  # Less than 10MB growth

    assert "All NLP operations completed within memory constraints"

if __name__ == '__main__':
    pytest.main([__file__])
