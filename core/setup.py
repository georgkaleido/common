"""Remove.bg Core Lib
"""
from pathlib import Path
from setuptools import setup
from pkg_resources import parse_requirements

install_requires = []
with Path('requirements.txt').open() as requirements_txt:
  for line in requirements_txt:
    if not line.startswith('--'):
      install_requires.append(line)

# See setup.cfg
setup(
  setup_requires=['pbr>=2.5', 'setuptools>=17.1'],
  pbr=True,
  install_requires=install_requires,
  python_requires='>=3.6, <4'
)
