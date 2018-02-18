"""
source_plugin setup file
"""

from setuptools import setup, find_packages

setup(
    name='package-source-plugin',
    version='1.0',

    description='Provides the package index source services',

    author='Ajeet Singh',
    author_email='singajeet@gmail.com',

    url='http://githubpages.com/singajeet',


    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                ],

    platforms=['Any'],

    scripts=[],

    provides=['ui_developer.core.service.package.source_plugin',
             ],

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'ui_builder.core.service.package.sources': [
            'package_index_http = \
            ui_builder.core.service.package\
            .source_plugin:DefaultPackageSource',
        ],
    },

    zip_safe=False
)
