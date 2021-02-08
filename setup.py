from setuptools import setup

setup(
    name="apod",
    version="0.0.0",
    py_modules=["apod"],
    entry_points={"console_scripts": ["apod=apod.cli:cli"]},
)
