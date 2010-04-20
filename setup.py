from setuptools import setup, find_packages
import os

version = '0.1a1'

setup(
    name='slc.stickystatusmessages',
    version=version,
    description="Provides sticky status messages to members for all the folders in which they are assigned local roles",
    long_description=open("README.txt").read() + "\n" +
                    open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        ],
    keywords='statusmessage status sticky',
    author='JC Brand, Syslab.com GmbH',
    author_email='brand@syslab.com',
    url='http://plone.org/products/slc.stickystatusmessages',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir = {'' : 'src'},
    namespace_packages=['slc'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    entry_points="""
        [z3c.autoinclude.plugin]
        target = plone
    """,
    setup_requires=["PasteScript"],
    paster_plugins = ["ZopeSkel"],
    )
