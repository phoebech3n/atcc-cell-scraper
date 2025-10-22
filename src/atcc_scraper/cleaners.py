# ============================================================================
# cleaners.py - Text Cleaning Functions
# ============================================================================

import re
import nltk
from nltk.tokenize import sent_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng')


class TextCleaner:
    """Utilities for cleaning and normalizing text"""
    
    UNICODE_REPLACEMENTS = {
        '\xa0': '',
        '\xad': '',
        '\u00a0': ' ',
        '\u2264': 'less than or equal to ',
        '\u2265': 'greater than or equal to ',
        '\u00b1': 'plus/minus ',
        '\u2013': '-'
    }
    
    @staticmethod
    def clean_text(text):
        """Clean text by removing unicode characters and normalizing whitespace"""
        if not text:
            return None
        
        # Replace unicode characters
        for unicode_char, replacement in TextCleaner.UNICODE_REPLACEMENTS.items():
            text = text.replace(unicode_char, replacement)
        
        # Tokenize sentences and strip whitespace
        sentences = sent_tokenize(text)
        stripped_sentences = [sent.strip() for sent in sentences]
        text = ' '.join(stripped_sentences)
        
        # Handle temperature unicode (e.g., 37°C)
        text = re.sub(r'(\d+)\u00b0C', r'\1 degrees Celsius', text)
        
        # Remove ATCC product references
        text = re.sub(r' \(([^;]+);\s*ATCC\s([^\)]+)\)', '', text)
        text = re.sub(r' \(ATCC\s([^\)]+)\)', '', text)
        
        return text
    
    @staticmethod
    def clean_list(items):
        """Clean a list of text items"""
        return [TextCleaner.clean_text(item) for item in items if item.strip()]
    
    @staticmethod
    def normalize_html_tags(soup):
        """Normalize superscript and subscript tags in BeautifulSoup"""
        for sup in soup.find_all('sup'):
            sup.string = '^' + sup.get_text()
            sup.unwrap()
        
        for sub in soup.find_all('sub'):
            sub.string = '_' + sub.get_text()
            sub.unwrap()