"""
ATCC Cell Scraper - Web scraping tool for ATCC cell line data
"""

__version__ = "0.1.0"
__author__ = "Phoebe Chen"

# Make main classes easily importable
from .main import ATCCPipeline
from .scraper import ATCCScraper, ScraperFactory
from .config import Config

__all__ = [
    'ATCCPipeline',
    'ATCCScraper', 
    'ScraperFactory',
    'Config',
]