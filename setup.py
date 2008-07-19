from setuptools import setup, find_packages

version = '0.1'

setup(name='five.pt',
      version=version,
      description="Five bridges for the z3c.pt package.",
      long_description=open("README.txt").read() + open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Hanno Schlichting',
      author_email='hannosch@gmail.com',
      url='',
      license='ZPL',
      namespace_packages=['five'],
      packages = find_packages('src'),
      package_dir = {'':'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.pt',
      ],
      )
