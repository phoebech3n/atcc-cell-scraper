# ============================================================================
# config.py - Configuration and Constants
# ============================================================================

class Config:
    """Configuration settings for ATCC scraper"""
    
    # Scraping parameters
    TOTAL_CELLS = 1655
    CELLS_PER_PAGE = 48 # 24 or 48
    CELLS_ON_LAST_PAGE = TOTAL_CELLS % CELLS_PER_PAGE

    # URLs
    BASE_URL = 'https://www.atcc.org'
    SEARCH_URL = f'{BASE_URL}/cell-products/animal-cells#t=productTab&numberOfResults={CELLS_PER_PAGE}&f:Productcategory=[Animal%20cells]'
    
    # Timeouts and waits
    PAGE_LOAD_TIMEOUT = 10
    STANDARD_WAIT = 10
    LAST_PAGE_WAIT = 60
    
    # CSS Selectors
    class Selectors:
        CELL_LIST = 'coveo-list-layout'
        PRODUCT_CARD = 'product-search-listing-card__name'
        RESULT_LINK = 'CoveoResultLink'
        NEXT_BUTTON_WRAPPER = 'pagination__page--next'
        NEXT_BUTTON = 'pagination__button'
        BASIC_INFO_COL = 'pdp-page-two-columns__col-1'
        INFO_TITLE = 'product-information__title'
        INFO_DATA = 'product-information__data'
        ACCORDION_ITEM = 'generic-accordion__item-title-text'
        INFO_LIST = 'product-information__list'
        IMAGE_GALLERY = 'modal-image-gallery__open-modal'
        PRICE_CURRENT = 'product-pricing__current-price'
    
    # File paths
    LINKS_FILE = 'output_data/cell_names_links.json'
    OUTPUT_DIR = 'output_data/cell_protocols'
    MERGED_FILE = 'output_data/cell_protocols.json'
