"""
Scan Singularity container images using CoreOS Clair.
"""
from setuptools import find_packages, setup

dependencies = ['click', 'six', 'requests', 'texttable']

setup(
    name='clair_singularity',
    version='0.3.0',
    url='https://github.com/dctrud/clair-singularity',
    author='David Trudgian',
    author_email='dtrudg@sylabs.io',
    description='Scan Singularity container images using CoreOS Clair.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'pytest-flake8'],
    entry_points={
        'console_scripts': [
            'clair-singularity = clair_singularity.cli:cli',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Quality Assurance',
    ]
)
