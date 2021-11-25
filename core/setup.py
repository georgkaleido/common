"""Remove.bg Core Lib"""

from pkg_resources import parse_requirements
from setuptools import setup

with open("requirements.in") as requirements_in:
    requirements = [line for line in requirements_in if not line.startswith("--")]

install_requires = [str(requirement) for requirement in parse_requirements(requirements)]

# See setup.cfg
setup(
    setup_requires=["pbr>=2.5", "setuptools>=17.1"],
    pbr=True,
    install_requires=install_requires,
    python_requires=">=3.6",
)
