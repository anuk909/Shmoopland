from setuptools import setup, find_packages

setup(
    name="shmoopland",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0.0",
        "spacy>=3.8.0",
        "textblob>=0.18.0",
        "markovify>=0.9.0",
        "memory-profiler>=0.61.0",
        "pytest>=7.4.0",
    ],
    python_requires=">=3.8",
)
