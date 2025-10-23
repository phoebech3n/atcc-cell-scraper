from setuptools import setup, find_packages

setup(
    name='atcc-scraper',
    version='0.1.0',
    author='Phoebe Chen',
    author_email='phoebeche3n@gmail.com', 
    description='Modular web scraper for ATCC cell line data',
    url='https://github.com/phoebech3n/atcc-cell-scraper',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.8',
    install_requires=[
        'selenium>=4.0.0',
        'beautifulsoup4>=4.11.0',
        'requests>=2.28.0',
        'webdriver-manager>=3.8.0',
        'lxml>=4.9.0',
        'nltk>=3.8.0',
    ],
)