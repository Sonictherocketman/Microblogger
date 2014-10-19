from distutils.core import setup

setup(
    name='Microblogger',
    version='0.0.1',
    author='Brian Schrader',
    author_email='brian@biteofanapple.com',
    packages=['microblogger', 'microblogger.test'],
    scripts=[], # TODO: Add bin/ scripts here.
    url='https://github.com/Sonictherocketman/Microblogger',
    license='LICENSE.txt',
    description='The first microblogging service implementing the Open Microblog standard. It is intended to be a base implementation of the standard; a proof of concept for the standard.',
    long_description=open('README.md').read(),
    install_requires=[
        ],
    )