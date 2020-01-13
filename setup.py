import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='switchinfo',
    version='1.1',
    packages=find_packages(),
    include_package_data=True,
    license='GPL',
    description='A tool to show what is connected to switch ports',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/datagutten/switchinfo',
    author='Anders Birkenes',
    author_email='datagutten@datagutten.net',
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ], install_requires=['django', 'easysnmp', 'requests']
)
