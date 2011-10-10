from setuptools import setup, find_packages

version = '2.2.0'

setup(name='five.pt',
      version=version,
      description="Five bridges and patches to use Chameleon with Zope 2.",
      long_description=open("README.txt").read() + "\n" + open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Hanno Schlichting, Malthe Borch and the Zope community',
      author_email='zope-dev@zope.org',
      url='',
      license='ZPL',
      namespace_packages=['five'],
      packages = find_packages('src'),
      package_dir = {'':'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'sourcecodegen>=0.6.14',
          'z3c.pt>=2.1.4',
          'zope.pagetemplate>=3.6.2',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
