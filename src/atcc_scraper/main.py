# ============================================================================
# main.py - Main Orchestration Script
# ============================================================================

import json
import os
from tqdm import tqdm
from typing import Optional

from config import Config
from scraper import ATCCScraper
from exporters import DataExporter
from parsers import *

class ATCCPipeline:
    """Main pipeline for scraping and processing ATCC cell data"""
    
    def __init__(self):
        """Initialize pipeline with output directory"""
        self.output_dir = Config.OUTPUT_DIR
        self.links_file = Config.LINKS_FILE
        self.merged_file = Config.MERGED_FILE
        self.unscraped_cells = {}
    
    def scrape_links(self, driver):
        """Step 1: Scrape all cell links from ATCC website"""
        print("=" * 60)
        print("STEP 1: Scraping cell links from ATCC website")
        print("=" * 60)
        
        scraper = ATCCScraper(driver)
        links_dict = scraper.scrape_cell_links()
        
        print(f"\nTotal cells found: {len(links_dict)}")
        print(f"Repeated cells: {len(scraper.repeated_cells)}")
        
        # Save links to file
        DataExporter.save_links(links_dict, self.links_file)
        print(f"Links saved to {self.links_file}\n")
        
        return links_dict
    
    def process_cells(self, links_dict, start_key=None):
        """Step 2: Process each cell and extract data"""
        print("=" * 60)
        print("STEP 2: Processing cell data")
        print("=" * 60)
        
        total_cells = len(links_dict)
        cell_id = 1
        
        # Handle resume from specific cell
        iterator = iter(links_dict.items())
        if start_key:
            for cell_name, url in iterator:
                if cell_name == start_key:
                    print(f"Resuming from: {cell_name} (ID: {cell_id})")
                    break
                cell_id += 1
        
        # Process each cell
        for cell_name, url in tqdm(iterator, desc="Scraping cells", ncols=100):
            cell_file_path = os.path.join(self.output_dir, cell_name + ".json")

            # first check if the cell information was already extracted
            if not os.path.exists(cell_file_path):
                try:
                    tqdm.write(f"[{cell_id}/{total_cells}] Processing: {cell_name}...")
                    # Scrape page
                    soup = ATCCScraper.scrape_cell_page(url)
                    if not soup:
                        tqdm.write("FAILED (scraping error)")
                        cell_id += 1
                        continue
                    
                    # Parse data
                    atcc_num = url.split('/')[-1].upper()
                    cell_protocol = self._parse_cell_data(soup, cell_name, atcc_num, cell_id, url)
                    tqdm.write(f"Parsed {cell_name}. Saving file...", end=" ")
                    
                    # Save to file
                    DataExporter.save_cell_protocol(cell_name, cell_protocol, self.output_dir)
                    
                    tqdm.write("✓")
                    cell_id += 1
                    tqdm.write('-' * 60)
                    
                except Exception as e:
                    tqdm.write(f"FAILED ({e})")
                    cell_id += 1
                    continue
            else:
                tqdm.write(f"Already extracted {cell_name} information.")
        
        print(f"\nProcessing complete! Data saved to {self.output_dir}/")
        if len(self.unscraped_cells) > 0:
            print(f"{len(self.unscraped_cells)} cells failed during scraping: {self.unscraped_cells}")
        else:
            print("All cells successfully scraped.")
    
    def _parse_cell_data(self, soup, cell_name, atcc_num, cell_id, url):
        """Parse all data for a single cell"""
        # Basic information
        cell_protocol = BasicInfoParser.parse(soup, cell_name, atcc_num, cell_id)
        tqdm.write("Basic info ✓")
        
        # Handling information
        handling_info = HandlingInfoParser.parse(soup)
        cell_protocol.update(handling_info)
        tqdm.write("Handling info ✓")
        
        # Images
        cell_protocol['Images'] = ImageParser.extract_images(soup)
        tqdm.write("Images ✓")
        
        # Price
        cell_protocol['Price'] = PriceParser.extract_price(soup)
        tqdm.write("Price ✓")
        
        # URL
        cell_protocol['ATCC Link'] = url
        tqdm.write("URL ✓")
        
        return cell_protocol
    
    def merge_all_protocols(self):
        """Step 3: Merge all individual JSON files into one dataset"""
        print("=" * 60)
        print("STEP 3: Merging all protocols")
        print("=" * 60)
        
        merged_data = DataExporter.merge_protocols(self.output_dir, self.merged_file)
        
        print(f"Merged {len(merged_data)} cell protocols")
        print(f"Saved to {self.merged_file}\n")
        
        return merged_data
    
    def run_full_pipeline(self, driver, scrape_links=True):
        """Run complete pipeline: scrape links -> process cells -> merge"""
        # Step 1: Scrape links
        if scrape_links:
            links_dict = self.scrape_links(driver)
        else:
            with open(self.links_file, 'r') as f:
                links_dict = json.load(f)           
        
        # Step 2: Process cells
        self.process_cells(links_dict)
        
        # Step 3: Merge protocols
        self.merge_all_protocols()
        
        print("=" * 60)
        print("PIPELINE COMPLETE!")
        print("=" * 60)


# ============================================================================
# Usage Examples
# ============================================================================

def example_usage_colab():
    """Example: Running on Google Colab"""
    import google_colab_selenium as gs
    
    # Initialize pipeline
    pipeline = ATCCPipeline()
    
    # Create driver
    driver = gs.Chrome()
    
    # Run full pipeline
    pipeline.run_full_pipeline(driver, scrape_links=True)


def example_usage_local():
    """Example: Running locally with Chrome"""
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    
    # Setup Chrome options
    options = Options()
    options.add_argument("--headless=new")
    
    # Setup WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Initialize pipeline
    pipeline = ATCCPipeline()
    
    # Run full pipeline
    pipeline.run_full_pipeline(driver,scrape_links=True)


def example_process_only():
    """Example: Only process cells (links already scraped)"""
    pipeline = ATCCPipeline()
    
    # Process all cells
    pipeline.process_cells()
    
    # Or resume from specific cell
    # pipeline.process_cells(start_key='Specific Cell Name')
    
    # Merge all protocols
    pipeline.merge_all_protocols()


def example_update_prices():
    """Example: Update prices for existing protocols"""
    pipeline = ATCCPipeline()
    
    # Load existing data
    with open('cell_names_links.json', 'r') as f:
        links_dict = json.load(f)
    
    with open('cell_protocols.json', 'r') as f:
        protocols = json.load(f)
    
    # Update prices
    count = 0
    total = len(links_dict)
    
    for cell_name, url in links_dict.items():
        count += 1
        print(f"[{count}/{total}] Updating price for {cell_name}...", end=' ')
        
        soup = ATCCScraper.scrape_cell_page(url)
        if soup:
            price = PriceParser.extract_price(soup)
            protocols[cell_name]['Price'] = price
            protocols[cell_name]['ATCC Link'] = url
            print("✓")
        else:
            print("FAILED")
    
    # Save updated data
    with open('cell_protocols.json', 'w') as f:
        json.dump(protocols, f, indent=4)
    
    print(f"\nPrice update complete!")


def example_scrape_single_cell():
    """Example: Scrape a single cell for testing"""
    url = 'https://www.atcc.org/products/crl-1658'
    
    # Scrape the page
    soup = ATCCScraper.scrape_cell_page(url)
    
    if soup:
        # Parse data
        cell_name = "Test Cell"
        atcc_num = url.split('/')[-1].upper()
        cell_id = 1
        
        # Basic info
        basic_info = BasicInfoParser.parse(soup, cell_name, atcc_num, cell_id)
        print("Basic Info:", json.dumps(basic_info, indent=2))
        
        # Handling info
        handling_info = HandlingInfoParser.parse(soup)
        print("\nHandling Info:", json.dumps(handling_info, indent=2))
        
        # Images
        images = ImageParser.extract_images(soup)
        print("\nImages:", images)
        
        # Price
        price = PriceParser.extract_price(soup)
        print("\nPrice:", price)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    """
    Main entry point - uncomment the example you want to run
    """
    
    # ==================================================================
    # OPTION 1: Full pipeline on Google Colab
    # ==================================================================
    # import google_colab_selenium as gs
    # driver = gs.Chrome()
    # pipeline = ATCCPipeline()
    # pipeline.run_full_pipeline(driver, scrape_links=True)
    
    # ==================================================================
    # OPTION 2: Full pipeline locally
    # ==================================================================
    example_usage_local()
    
    # ==================================================================
    # OPTION 3: Process only (links already scraped)
    # ==================================================================
    # example_process_only()
    
    # ==================================================================
    # OPTION 4: Update prices only
    # ==================================================================
    # example_update_prices()
    
    # ==================================================================
    # OPTION 5: Test with single cell
    # ==================================================================
    # example_scrape_single_cell()
    
    # ==================================================================
    # OPTION 6: Custom pipeline
    # ==================================================================
    # pipeline = ATCCPipeline(output_dir='my_custom_output')
    # 
    # # Step 1: Scrape links
    # import google_colab_selenium as gs
    # driver = gs.Chrome()
    # links = pipeline.scrape_links(driver)
    # 
    # # Step 2: Process cells (can resume if interrupted)
    # pipeline.process_cells()
    # # Or resume from specific cell:
    # # pipeline.process_cells(start_key='Cell Name Here')
    # 
    # # Step 3: Merge all data
    # pipeline.merge_all_protocols()
    
    print("Please uncomment one of the options above to run the script.")
    print("See the Usage Examples section for more details.")