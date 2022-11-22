#!/usr/bin/env python3
import os
from setuptools import setup

with open("/README.md") as f:
    readme = f.read()

URL = "https://gitlab.com/qwolphin/wast"

PROJECT_URLS = {
    "Documentation": "https://wast.dev",
    "Source Code": URL,
    "Bug Tracker": URL + "/issues",
    "Author Website": "https://LumiAkimova.com",
}

setup(
    name="wast",
    version=os.environ["WAST_VERSION"],
    description="Improved AST for Python focused on code generation",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Lumi Akimova",
    author_email="lumi.akimova@gmail.com",
    url=URL,
    project_urls=PROJECT_URLS,
    packages=["wast"],
    package_data={"wast": ["py.typed"]},
    zip_safe=False,
    install_requires=["attrs>=21.3.0"],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
    ],
)
