from setuptools import setup, find_packages

setup(
    name="shmoopland",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0.0",
    ],
    python_requires=">=3.8",
)
