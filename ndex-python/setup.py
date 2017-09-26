"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

def get_long_description():
    with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
    return long_description

if __name__ == '__main__':
    setup(
        name='ndex',

        # Versions should comply with PEP440.  For a discussion on single-sourcing
        # the version across setup.py and the project code, see
        # https://packaging.python.org/en/latest/single_source_version.html
        version='3.0.11.23',

        description='NDEx Python includes a client and a data model.',
        long_description=get_long_description(),

        # The project's main homepage.
        url='https://www.ndexbio.org',

        # Author details
        author='The NDEx Project',
        author_email='contact@ndexbio.org',

        # Choose your license
        license='BSD',

        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 5 - Production/Stable',

            # Indicate who your project is intended for
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Topic :: Scientific/Engineering :: Medical Science Apps.',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: BSD License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 2.7',
        ],

        # What does your project relate to?
        keywords='network analysis biology',

        # You can just specify the packages manually here if your project is
        # simple. Or you can use find_packages().
        packages=find_packages(exclude=[]),

        install_requires = [
            'requests',
            'requests_toolbelt',
            'networkx',
            'urllib3>=1.16'
        ],
    
        include_package_data=True

    )
