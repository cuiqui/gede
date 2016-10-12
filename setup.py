from setuptools import setup

setup(
    name='gede',
    version='0.1',
    author='Juan Schandin',
    author_email='jschandin@gmail.com',
    py_modules=['gede'],
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points="""
    [console_scripts]
    gede = gede:cli
    """
)
