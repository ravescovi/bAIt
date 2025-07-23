"""
Setup script for my_beamline - Example beamline package
Created by bAIt tutorial system
"""

from setuptools import setup, find_packages

setup(
    name="my_beamline",
    version="0.1.0",
    description="Example beamline instrument package for BITS tutorial",
    author="Tutorial User",
    author_email="user@example.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "bluesky",
        "ophyd", 
        "databroker",
        "apsbits",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
        ]
    },
    entry_points={
        "console_scripts": [
            "my_beamline=my_beamline.startup:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)