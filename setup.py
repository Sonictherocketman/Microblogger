from distutils.core import setup
# TODO
setup(
    name='Microblogger',
    version='0.0.1',
    author='Brian Schrader',
    author_email='brian@biteofanapple.com',
    packages=['microblogger', 'microblogger.test'],
    scripts=[], # TODO: Add bin/ scripts here.
    url='', # TODO: Add
    license='LICENSE.txt',
    description='', # TODO: Add
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.1.1"
        ],
    )