from setuptools import setup, find_packages
from collections import OrderedDict

long_description="""
Read more at the Battlecode website: https://play.battlecode.org.
"""

setup(name='battlecode2025',
      version="25.0.0",
      description='Battlecode 2025 game engine.',
      author='Battlecode',
      long_description=long_description,
      author_email='battlecode@mit.edu',
      url="https://play.battlecode.org",
      license='MIT',
      packages=find_packages(),
      project_urls=OrderedDict((
          #('Code', 'https://github.com/battlecode/battlecode25/tree/master/engine'),
          #('Documentation', 'https://github.com/battlecode/battlecode25/tree/master/engine')
      )),
      install_requires=[
            'RestrictedPython==7.4',
            'flatbuffers==24.3.25'
      ],
      python_requires='>=3.11',
      zip_safe=False,
)
