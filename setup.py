#!/usr/bin/env python3
"""Setup script for p1person package."""

from setuptools import setup, find_packages
import os

# Read version from p1person.py
VERSION = "0.2"

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="p1person",
    version=VERSION,
    author="Your Name",
    author_email="your.email@example.com",
    description="PingOne Custom Attribute Management Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/p1person",
    py_modules=[
        "p1person",
        "config_manager",
        "pingone_client",
        "attribute_manager",
        "logger",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "p1person=p1person:main",
        ],
    },
    include_package_data=True,
    keywords="pingone ldap inetorgperson attributes identity management",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/p1person/issues",
        "Source": "https://github.com/yourusername/p1person",
        "Documentation": "https://github.com/yourusername/p1person#readme",
    },
)
