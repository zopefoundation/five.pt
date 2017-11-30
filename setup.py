from setuptools import setup, find_packages


setup(
    name='five.pt',
    version='3.0',
    description="DEPRECATED: Five bridges and patches to use Chameleon with"
                " Zope.",
    long_description=(open("README.rst").read() + "\n" +
                      open("CHANGES.rst").read()),
    classifiers=[
        "Development Status :: 7 - Inactive",
        "Framework :: Zope :: 4",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    keywords='',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    url='https://github.com/zopefoundation/five.pt',
    license='ZPL',
    namespace_packages=['five'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Zope2 >= 4.0a2',
    ],
)
