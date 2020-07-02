import os

from setuptools import setup
from setuptools.command.test import test as TestCommand

version = '0.11.2'


def read_file(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fp:
        return fp.read()


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        os.chdir('ogmios_tests')
        pytest.main(self.test_args)


setup(name='django-ogmios',
      version=version,
      author="Fusionbox, Inc.",
      author_email="programmers@fusionbox.com",
      url="https://github.com/fusionbox/django-ogmios",
      keywords="email send easy simple helpers django",
      description="Just sends email. Simple, easy, multiformat.",
      long_description=read_file('README.rst') + '\n\n' + read_file('CHANGELOG.rst'),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Communications :: Email',
          'Topic :: Software Development :: Libraries'
      ],
      install_requires=[
          'Django>=1.11',
          'PyYAML',
          'Markdown',
          'html2text',
          'six',
      ],
      tests_require=['pytest-django', 'pytest-pythonpath', 'pytest'],
      cmdclass={'test': PyTest},
      packages=['ogmios'],
      )
