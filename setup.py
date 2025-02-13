import os
from setuptools import setup, find_packages


def read(*paths):
    """Read the contents of a text fil safely.
    >>> read("project_name", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    rootpath = os.path.dirname(__file__)
    filepath = os.path.join(rootpath, *paths)
    with open(filepath) as file_:
        return file_.read().strip()


def read_requirements(path):
    """Return a list of requirements from a text file."""
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(("#", "git+", '"', "-"))
    ]


setup(
    name="giovannipad-dundie",
    version="0.1.1",
    description="Reward point system for Dunder Mifflin",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Giovanni Padilha",
    python_requires=">=3.10",
    packages=find_packages(exclude=["integration"]),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "dundie = dundie:__main__.main"
        ]
    },
    install_requires=read_requirements("requirements/requirements.txt"),
    extras_require={
        "test": read_requirements("requirements/requirements.test.txt"),
        "dev": read_requirements("requirements/requirements.dev.txt"),
    }
)
