from setuptools import setup

setup(
    name='depl',
    version='0.1',
    author='Juan Schandin',
    author_email='jschandin@gmail.com',
    py_modules=['depl'],
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points="""
    [console_scripts]
    depl = depl:cli
    """
)
