# ============================================================================
# scraper.py - Web Scraping Logic
# ============================================================================

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

from .config import Config

class ATCCScraper:
    """Main scraper class for ATCC website"""
    
    def __init__(self, driver):
        """
        Initialize scraper with Selenium driver
        
        Args:
            driver: Selenium WebDriver instance (Chrome, Firefox, etc.)
        """
        self.driver = driver
        self.cells_dict = {}
        self.seen_cells = set()
        self.repeated_cells = []
    
    def scrape_cell_links(self):
        """
        Scrape all cell product links from ATCC website
        
        Returns:
            dict: Dictionary mapping cell names to their URLs
        """
        self.driver.get(Config.SEARCH_URL)
        
        iteration = 0
        cells_per_page = Config.CELLS_PER_PAGE
        
        while True:
            iteration += 1
            print(f"Iteration: {iteration}")
            
            # Wait for page to load
            WebDriverWait(self.driver, Config.PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, Config.Selectors.CELL_LIST))
            )

            if iteration == 1:
                try:
                    cookies_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Use necessary cookies')]")
                    cookies_button.click()
                    print("Cleared cookies banner!")
                except:
                    print("Cookies banner not found!")
            
            # Find next button
            next_button_wrapper = self.driver.find_element(
                By.CLASS_NAME, 
                Config.Selectors.NEXT_BUTTON_WRAPPER
            )
            next_button = next_button_wrapper.find_element(
                By.CLASS_NAME, 
                Config.Selectors.NEXT_BUTTON
            )
            
            # Wait for all cells to load on current page
            cell_objects = self._wait_for_cells(next_button, cells_per_page)
            print(f"Loaded {len(cell_objects)} cells")
            
            # Extract cell information from current page
            self._extract_cell_data(cell_objects)
            
            print(f"Repeated cells so far: {len(self.repeated_cells)}")
            print(f"Total unique cells: {len(self.cells_dict)}\n")
            
            # Check if we're on the last page
            if next_button.get_attribute('disabled'):
                print("Reached last page!")
                break
            
            # Click next and wait
            next_button.click()
            time.sleep(Config.STANDARD_WAIT)
        
        self.driver.quit()
        return self.cells_dict
    
    def _wait_for_cells(self, next_button, expected_count):
        """
        Wait for all cells to load on the current page
        
        Args:
            next_button: Selenium element for the next page button
            expected_count: Expected number of cells per page
            
        Returns:
            list: List of cell web elements
        """
        while True:
            cell_objects = self.driver.find_elements(
                By.CLASS_NAME, 
                Config.Selectors.CELL_LIST
            )
            
            # Not on last page - expect full page of cells
            if not next_button.get_attribute('disabled'):
                if len(cell_objects) != expected_count:
                    time.sleep(Config.STANDARD_WAIT)
                else:
                    break
            # On last page - may have fewer cells
            else:
                time.sleep(Config.LAST_PAGE_WAIT)
                cell_objects = self.driver.find_elements(
                    By.CLASS_NAME, 
                    Config.Selectors.CELL_LIST
                )
                break
        
        return cell_objects
    
    def _extract_cell_data(self, cell_objects):
        """
        Extract cell names and links from loaded elements
        
        Args:
            cell_objects: List of Selenium web elements containing cell data
        """
        for cell_object in cell_objects:
            try:
                # Find the product card
                product_card = cell_object.find_element(
                    By.CLASS_NAME, 
                    Config.Selectors.PRODUCT_CARD
                )
                
                # Find the link element
                link_element = product_card.find_element(
                    By.CLASS_NAME, 
                    Config.Selectors.RESULT_LINK
                )
                
                # Extract link and cell name
                link = link_element.get_attribute('href')
                cell_name = link_element.text
                
                # Track duplicates for debugging
                if cell_name in self.seen_cells:
                    self.repeated_cells.append(cell_name)
                
                self.seen_cells.add(cell_name)
                self.cells_dict[cell_name] = link
                
            except Exception as e:
                print(f"Error extracting cell data: {e}")
                continue
    
    @staticmethod
    def scrape_cell_page(url, timeout=10):
        """
        Scrape individual cell product page using requests
        
        Args:
            url: URL of the cell product page
            timeout: Request timeout in seconds
            
        Returns:
            BeautifulSoup: Parsed HTML soup object, or None if error
        """
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {url}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error scraping {url}: {e}")
            return None
    
    def get_statistics(self):
        """
        Get scraping statistics
        
        Returns:
            dict: Statistics about the scraping session
        """
        return {
            'total_unique_cells': len(self.cells_dict),
            'total_seen_cells': len(self.seen_cells),
            'repeated_cells_count': len(self.repeated_cells),
            'unique_repeated_cells': len(set(self.repeated_cells)),
            'repeated_cells_list': self.repeated_cells
        }


class ScraperFactory:
    """Factory for creating scraper instances with different drivers"""
    
    @staticmethod
    def create_colab_scraper():
        """
        Create scraper for Google Colab environment
        
        Returns:
            ATCCScraper: Scraper instance with Colab driver
        """
        try:
            import google_colab_selenium as gs
            driver = gs.Chrome()
            return ATCCScraper(driver)
        except ImportError:
            raise ImportError(
                "google_colab_selenium not available. "
                "Install with: !pip install google_colab_selenium"
            )
    
    @staticmethod
    def create_local_scraper(headless=True):
        """
        Create scraper for local environment
        
        Args:
            headless: Whether to run browser in headless mode
            
        Returns:
            ATCCScraper: Scraper instance with local Chrome driver
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Setup Chrome options
            options = Options()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Setup WebDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            return ATCCScraper(driver)
            
        except ImportError:
            raise ImportError(
                "Required packages not available. Install with: "
                "pip install selenium webdriver-manager"
            )


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == "__main__":
    """Examples of using the scraper"""
    
    # Example 1: Basic usage with Google Colab
    # import google_colab_selenium as gs
    # driver = gs.Chrome()
    # scraper = ATCCScraper(driver)
    # links = scraper.scrape_cell_links()
    # print(f"Scraped {len(links)} cell links")
    
    # Example 2: Using factory for Colab
    # scraper = ScraperFactory.create_colab_scraper()
    # links = scraper.scrape_cell_links()
    # stats = scraper.get_statistics()
    # print(stats)
    
    # Example 3: Using factory for local
    # scraper = ScraperFactory.create_local_scraper(headless=True)
    # links = scraper.scrape_cell_links()
    
    # Example 4: Scraping single page
    # url = 'https://www.atcc.org/products/crl-1658'
    # soup = ATCCScraper.scrape_cell_page(url)
    # if soup:
    #     print("Successfully scraped page!")
    #     print(f"Title: {soup.title.string}")
    
    print("See examples in comments above")