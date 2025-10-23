# ATCC Cell Scraper

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A modular, production-ready Python package for scraping and processing cell line protocol data from the [ATCC (American Type Culture Collection)](https://www.atcc.org/) website.

## 🌟 Overview

This project extracts detailed information about 1,000+ animal cell lines, including:
- Cell characteristics and classifications
- Complete handling procedures
- Subculturing protocols  
- Growth conditions and medium requirements
- Pricing and availability
- Product images

### Why This Project?

During my internship with Whelix (Former Mito Robotics), I needed structured, programmatic access to ATCC cell line data. This scraper transforms scattered web data into clean, analyzable JSON format for downstream analysis and machine learning model development.

## ✨ Key Features

- **🏗️ Modular Architecture** - Separation of concerns with 6 specialized modules
- **🔄 Robust Parsing** - Handles structured and unstructured procedure formats
- **🧹 Intelligent Text Cleaning** - Unicode normalization, NLTK-based sentence parsing
- **💾 Flexible Export** - Individual JSON files or merged dataset
- **⚡ Resume Capability** - Continue interrupted scraping sessions
- **🔌 Dual Driver Support** - Works locally and in Google Colab

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/phoebech3n/atcc-cell-scraper.git
cd atcc-cell-scraper

# Install package in development mode
pip install -e .

# Or install with all dependencies
pip install -e ".[all]"
```

### Basic Usage

```python
from atcc_scraper import ATCCPipeline

# Initialize pipeline
pipeline = ATCCPipeline()

# Create driver (local)
from atcc_scraper.scraper import ScraperFactory
scraper = ScraperFactory.create_local_scraper(headless=True)
driver = scraper.driver

# Run full pipeline
pipeline.run_full_pipeline(driver)
```


## 📁 Project Structure

```
atcc-cell-scraper/
├── src/atcc_scraper/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration and constants
│   ├── scraper.py           # Selenium-based web scraping
│   ├── parsers.py           # HTML parsing (BeautifulSoup)
│   ├── cleaners.py          # Text cleaning utilities
│   ├── exporters.py         # JSON export functionality
│   └── main.py              # Pipeline orchestration
├── tests/                   # Unit tests (coming soon)
├── examples/                # Usage examples
├── docs/                    # Additional documentation
├── requirements.txt         # Python dependencies
├── setup.py                 # Package installation config
└── README.md                # This file
```

## 🏛️ Architecture

The scraper follows a modular pipeline architecture:

```
┌─────────────┐    ┌───────────────┐    ┌─────────────┐    ┌─────────────┐
│   Scraper   │───▶│    Parsers    │───▶│  Cleaners   │───▶│  Exporters  │
│  (Selenium) │    │(BeautifulSoup)│    │   (NLTK)    │    │   (JSON)    │
└─────────────┘    └───────────────┘    └─────────────┘    └─────────────┘
       │                                                          │
       │                    ┌──────────────┐                      │
       └───────────────────▶│    Config    │◀─────────────────────┘
                            └──────────────┘
                                   ▲
                                   │
                            ┌──────────────┐
                            │   Main.py    │
                            │  (Pipeline)  │
                            └──────────────┘
```

### Module Responsibilities

- **`config.py`** - Centralized configuration (URLs, selectors, constants)
- **`scraper.py`** - Dynamic content loading with Selenium
- **`parsers.py`** - HTML parsing into structured data (4 parser classes)
- **`cleaners.py`** - Text normalization and cleaning utilities
- **`exporters.py`** - Data serialization and file management
- **`main.py`** - Pipeline orchestration

## 🔧 Technical Details

### Technologies Used

- **Web Scraping**: Selenium WebDriver, BeautifulSoup4
- **Text Processing**: NLTK (sentence tokenization, POS tagging)
- **Data Format**: JSON
- **Package Management**: setuptools

### Key Parsing Challenges Solved

1. **Mixed Format Procedures** - Handles both structured (numbered lists) and unstructured (paragraph) formats
2. **Unicode Normalization** - Converts temperature symbols, superscripts, and special characters
3. **Dynamic Content Loading** - Waits for JavaScript-rendered elements
4. **Duplicate Detection** - Tracks and reports cells during scraping

### Data Output Format

Here is an example output of a single cell:

```json
{
  "NIH/3T3": {
    "ID": 1,
    "Cell Name": "NIH/3T3",
    "ATCC Number": "CRL-3571",
    "Product category": "Animal cells",
    "Product type": ["Cell line"],
    "Organism": "Mus musculus, mouse",
    "Morphology": "fibroblast",
    "Tissue": "Embryo",
    "Applications": [
            "3D cell culture"
        ],
    "Growth properties": "adherent",
    "Complete medium": "...",
    "Temperature": "37 degrees Celsius",
    "Atmosphere": [
            "95% Air",
            "5% CO_2"
        ],
    "Handling procedure": {
      "Description": "...",
      "Procedure": {
        "1": "Thaw vial in 37°C water bath...",
        "2": "Transfer to culture flask..."
      }
    },
    "Subculturing procedure": {
      "Description": "...",
      "Procedure": {
        "1": "Remove and discard culture medium.",
        "2": "Briefly rinse the cell layer with..."
      }
    },
    "Medium renewal": "Every 2 to 3 days",
    "Reagents for cryopreservation": "Complete Growth Medium + 5% DMSO",
    "Images": null,
    "Price": 844.0,
    "ATCC Link": "https://www.atcc.org/products/crl-3571",
  }
}
```

See [Data Output Format](data_format.md) for more detailed information.

## 📊 Example Use Cases

- **Research Database** - Build searchable cell line database
- **Price Comparison** - Track pricing trends over time
- **Protocol Analysis** - Compare handling procedures across cell types
- **Metadata Extraction** - Generate training data for ML models
- **Lab Management** - Maintain inventory of available cell lines

## 🛠️ Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (coming soon)
pytest tests/

# Check coverage
pytest --cov=atcc_scraper tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

## 🗺️ Roadmap

- [ ] **Testing** - Comprehensive unit and integration tests
- [ ] **Logging** - Replace print statements with proper logging
- [ ] **Error Recovery** - Automatic retry logic for failed requests
- [ ] **CLI Interface** - Command-line tool for easy automation
- [ ] **Database Export** - SQLite/PostgreSQL export options
- [ ] **Async Scraping** - Parallel processing for faster execution
- [ ] **Docker Support** - Containerized deployment
- [ ] **CI/CD** - GitHub Actions for automated testing
- [ ] **Documentation** - Sphinx auto-generated docs

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Please respect ATCC's terms of service and robots.txt. Be considerate with scraping frequency to avoid overloading their servers.

## 🙏 Acknowledgments

- Data source: [ATCC (American Type Culture Collection)](https://www.atcc.org/)
- Built with: Selenium, BeautifulSoup, NLTK

## 📧 Link(s)

Project Link: [https://github.com/phoebech3n/atcc-cell-scraper](https://github.com/phoebech3n/atcc-cell-scraper)

