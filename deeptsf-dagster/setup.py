from setuptools import find_packages, setup

from setuptools import find_packages, setup
import os

# Get the current working directory
current_directory = os.getcwd()

# Get the parent directory
parent_directory = os.path.dirname(current_directory)

# Construct the path to the requirements.txt file in the parent directory
requirements_path = os.path.join(parent_directory, 'python_requirements.txt')

with open(requirements_path, "r") as f:
    python_requirements = f.read().splitlines()
    
setup(
    name="deeptsf_dagster",
    packages=find_packages(exclude=["deeptsf_dagster_tests"]),
    install_requires=python_requirements,
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
