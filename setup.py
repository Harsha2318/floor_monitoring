"""
Setup script for Employee Monitoring System
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="employee-monitoring-system",
    version="1.0.0",
    author="Floor Monitoring System",
    description="Local employee monitoring and workspace management system for MSMEs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/floor_monitoring",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "floor-monitoring=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*", "static/*", "static/**/*"],
    },
)
