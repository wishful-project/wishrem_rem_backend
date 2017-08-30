from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='rem_backend',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/wishful-project/wishrem_rem_backend',
    license='Apache 2.0',
    author='Daniel Denkovski, Valentin Rakovic',
    author_email='{danield, valentin}@feit.ukim.edu.mk',
    description='REM backend functions and events',
    long_description='REM backend functions and events',
    keywords='localization, interpolation, path loss, duty cycle, rrm events',
    #install_requires=['pyric', 'pyshark']
)
