from setuptools import setup, find_packages

version = '2.2.5'
__version__ = version

setup(
    name='five.pt',
    version=__version__,
    description="Five bridges and patches to use Chameleon with Zope.",
    long_description=(open("README.rst").read() + "\n" +
                      open("CHANGES.rst").read()),
    classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    keywords='',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    url='https://pypi.python.org/pypi/five.pt',
    license='ZPL',
    namespace_packages=['five'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'sourcecodegen>=0.6.14',
        'z3c.pt>=2.2',
        'zope.pagetemplate>=3.6.2',
        'Chameleon>=2.14',
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
