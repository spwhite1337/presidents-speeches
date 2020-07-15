from setuptools import setup, find_packages

setup(
    name='presidents-speeches',
    version='1.0',
    description='Search Engine for Presidential Speeches',
    author='Scott P. White',
    author_email='spwhite1337@gmail.com',
    packages=find_packages(),
    entry_points={'console_scripts': [
        'ps_download = presidents_speeches.download:download'
    ]},
    install_requires=[
        'requests',
        'beautifulsoup4',
        'lxml',
        'pandas',
        'numpy',
        'matplotlib',
        'ipykernel',
        'gensim',
        'Pillow',
        'tqdm'
    ]
)
