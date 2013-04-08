from os.path import exists
from setuptools import setup

setup(
name='symcode',
version='0.1-git',
author='Cristovao D. Sousa',
author_email='crisjss@gmail.com',
description='Library to collect sub-expressions from SymPy expressions and generate C and Python code',
license='BSD',
keywords='code sympy',
url='http://github.com/cdsousa/symcode',
packages=['symcode'],
long_description=open('README.md').read() if exists('README.md') else '',
classifiers=[
  'Development Status :: 4 - Beta',
  'Intended Audience :: Developers',
  'License :: OSI Approved :: BSD License',
  'Operating System :: OS Independent',
  'Programming Language :: Python',
  'Topic :: Software Development :: Code Generators',
  ],
)