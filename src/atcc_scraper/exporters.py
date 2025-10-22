# ============================================================================
# exporters.py - Data Export Functions
# ============================================================================

import json
import os
import re


class DataExporter:
    """Handle data export to JSON files"""
    
    @staticmethod
    def save_cell_protocol(cell_name, cell_data, output_dir):
        """Save individual cell protocol to JSON file"""
        # Sanitize filename
        filename = re.sub(r'[<>:"/\\|?*]', '_', f'{cell_name}.json')
        filepath = os.path.join(output_dir, filename)
        
        os.makedirs(output_dir, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({cell_name: cell_data}, f, indent=4)
    
    @staticmethod
    def save_links(links_dict, filename):
        """Save cell links dictionary to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(links_dict, f, indent=4)
    
    @staticmethod
    def merge_protocols(input_dir, output_file):
        """Merge all individual JSON files into one"""
        merged_data = {}
        
        for filename in os.listdir(input_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(input_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    cell_data = json.load(f)
                
                merged_data.update(cell_data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=4)
        
        return merged_data