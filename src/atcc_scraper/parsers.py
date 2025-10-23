# ============================================================================
# parsers.py - HTML Parsing Functions
# ============================================================================

import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

from .config import Config
from .cleaners import TextCleaner

class BasicInfoParser:
    """Parse basic cell information from product page"""
    
    @staticmethod
    def parse(soup, cell_name, atcc_num, cell_id):
        """Extract basic cell information"""
        cell_info_section = soup.find(class_=Config.Selectors.BASIC_INFO_COL)
        if not cell_info_section:
            return None
        
        titles = cell_info_section.find_all(class_=Config.Selectors.INFO_TITLE)
        data_items = cell_info_section.find_all(class_=Config.Selectors.INFO_DATA)
        
        cell_info = {
            'ID': cell_id,
            'Cell Name': cell_name,
            'ATCC Number': atcc_num
        }
        
        for title, data in zip(titles, data_items):
            title_text = title.text.strip()
            
            if title_text in ['Product type', 'Applications', 'Classification']:
                parsed_data = data.text.replace('\n', ',').split(',')
                parsed_data = TextCleaner.clean_list(parsed_data)
            elif title_text == "Tissue":
                parsed_data = data.text.split(';')
                parsed_data = TextCleaner.clean_list(parsed_data)
            else:
                parsed_data = TextCleaner.clean_text(data.text)
            
            cell_info[title_text] = parsed_data
        
        return cell_info


class ProcedureParser:
    """Parse handling and subculturing procedures"""
    
    @staticmethod
    def parse_structured_paragraph(text):
        """Parse procedures from structured paragraph format"""
        # Remove header
        text = re.sub(r'Handling Procedure for Frozen Cells', '', text, flags=re.IGNORECASE)
        
        step_counter = 0
        steps = {}
        description = []
        subculture_data = []
        current_step = []
        
        catalog_idx = text.find("CATALOG DESCRIPTION")
        if catalog_idx == -1:
            catalog_idx = len(text)
        
        for line in text[:catalog_idx].split("."):
            line = line.strip()
            
            if not line:
                continue
            
            # Check if line starts with a number
            if line.isdigit():
                if step_counter > 0:
                    steps[step_counter] = " ".join(current_step)
                    current_step = []
                step_counter += 1
            
            # Check for dash bullet points
            elif line and line[0] == "-":
                if step_counter > 0:
                    steps[step_counter] = " ".join(current_step)
                    current_step = []
                step_counter += 1
                current_step.append(line[1:].strip() + ".")
            
            else:
                # Part of description before steps
                if not steps and step_counter < 1:
                    description.append(line + ".")
                # Period between digits
                elif line and line[0].isdigit():
                    if current_step:
                        current_step[-1] += (line + ".")
                # Subculture procedure section
                elif 'subculture procedure' in line.lower():
                    line = re.sub(r'subculture procedure', '', line, flags=re.IGNORECASE)
                    subculture_data.append(line.strip() + ".")
                elif subculture_data:
                    subculture_data.append(line.strip() + ".")
                else:
                    current_step.append(line + ".")
        
        if current_step:
            steps[step_counter] = " ".join(current_step)
        
        return " ".join(description), steps, " ".join(subculture_data)
    
    @staticmethod
    def parse_unstructured_paragraph(text):
        """Parse procedures from unstructured paragraph format"""
        step_counter = 0
        steps = {}
        description = []
        current_step = []
        
        action_verbs = ["thaw", "remove", "allow", "add"]
        
        for line in sent_tokenize(text):
            line = line.strip()
            if not line:
                continue
            
            # Check if sentence starts with a verb
            pos_tags = nltk.pos_tag(word_tokenize(line))
            first_word = pos_tags[0][0].lower()
            
            if pos_tags[0][1] == 'VB' or first_word in action_verbs:
                if step_counter > 0:
                    steps[step_counter] = " ".join(current_step)
                    current_step = []
                step_counter += 1
                current_step.append(line)
            elif step_counter < 1 or ": " in line:
                description.append(line)
            else:
                current_step.append(line)
        
        if current_step:
            steps[step_counter] = " ".join(current_step)
        
        return " ".join(description), steps, None
    
    @staticmethod
    def parse(data_element):
        """Parse procedure from HTML element"""
        # Extract ordered list steps
        list_items = data_element.find_all('li')
        steps = {i + 1: TextCleaner.clean_text(item.text) for i, item in enumerate(list_items)}
        
        # Remove the ordered list from the element
        ol_tag = data_element.find("ol")
        if ol_tag:
            ol_tag.extract()
        
        text = data_element.text
        description = text
        subculture_info = None
        
        # If no bullet points, try parsing paragraph
        if not steps:
            if "handling procedure for frozen cells" in text.lower():
                description, steps, subculture_info = ProcedureParser.parse_structured_paragraph(text)
            else:
                description, steps, subculture_info = ProcedureParser.parse_unstructured_paragraph(text)
        
        return description, steps if steps else None, subculture_info


class HandlingInfoParser:
    """Parse handling and culture information"""
    
    @staticmethod
    def parse(soup):
        """Extract handling information from page"""
        TextCleaner.normalize_html_tags(soup)
        
        handling_info = {}
        subculture_info = None
        
        accordion_items = soup.find_all(class_=Config.Selectors.ACCORDION_ITEM)
        
        for item in accordion_items:
            if item.text == "Characteristics":
                HandlingInfoParser._parse_characteristics(item, handling_info)
            elif item.text == "Handling information":
                subculture_info = HandlingInfoParser._parse_handling_details(item, handling_info)
        
        return handling_info
    
    @staticmethod
    def _parse_characteristics(item, handling_info):
        """Parse characteristics section"""
        growth_prop = item.find_next(class_=Config.Selectors.INFO_TITLE)
        if growth_prop and growth_prop.text == "Growth properties":
            data = growth_prop.find_next(class_=Config.Selectors.INFO_DATA)
            handling_info["Growth properties"] = TextCleaner.clean_text(data.text)
    
    @staticmethod
    def _parse_handling_details(item, handling_info):
        """Parse handling information section"""
        info_list = item.find_next(class_=Config.Selectors.INFO_LIST)
        if not info_list:
            return None
        
        titles = info_list.find_all(class_=Config.Selectors.INFO_TITLE)
        data_items = info_list.find_all(class_=Config.Selectors.INFO_DATA)
        
        subculture_info = None
        
        for title, data in zip(titles, data_items):
            title_text = title.text
            
            if title_text == 'Unpacking and storage instructions':
                handling_info[title_text] = HandlingInfoParser._parse_steps(data)
            
            elif title_text == 'Complete medium':
                handling_info[title_text] = HandlingInfoParser._parse_medium(data)
            
            elif title_text == 'Temperature':
                handling_info[title_text] = TextCleaner.clean_text(data.text)
            
            elif title_text == 'Atmosphere':
                handling_info[title_text] = TextCleaner.clean_list(data.text.split(","))
            
            elif title_text == 'Handling procedure':
                desc, steps, subculture_info = ProcedureParser.parse(data)
                if desc or steps:
                    handling_info[title_text] = {
                        'Description': TextCleaner.clean_text(desc),
                        'Procedure': steps
                    }
            
            elif title_text == 'Subculturing procedure':
                subculture_info = HandlingInfoParser._parse_subculturing(
                    data, subculture_info, handling_info
                )
            
            else:
                handling_info[title_text] = TextCleaner.clean_text(data.text)
        
        return subculture_info
    
    @staticmethod
    def _parse_steps(data):
        """Parse numbered steps"""
        list_items = data.find_all('li')
        return {i + 1: TextCleaner.clean_text(item.text) for i, item in enumerate(list_items)}
    
    @staticmethod
    def _parse_medium(data):
        """Parse complete medium information"""
        parts = data.text.split(':\n')
        if len(parts) < 2:
            return TextCleaner.clean_text(parts[0])
        
        bullet_list = [item for item in parts[1].split('\n') if item]
        return TextCleaner.clean_text(f"{parts[0]}: {', '.join(bullet_list)}")
    
    @staticmethod
    def _parse_subculturing(data, subculture_info, handling_info):
        """Parse subculturing procedure"""
        list_items = data.find_all('li')
        steps = {i + 1: TextCleaner.clean_text(item.text) for i, item in enumerate(list_items)}
        
        # Remove ordered list
        ol_tag = data.find("ol")
        if ol_tag:
            ol_tag.extract()
        
        lines = data.text.splitlines() if steps else []
        
        # If no steps, try paragraph parsing
        if not steps:
            desc, steps, _ = ProcedureParser.parse_structured_paragraph(data.text)
            if not steps:
                desc, steps, _ = ProcedureParser.parse_unstructured_paragraph(data.text)
                lines = desc.splitlines()
            else:
                lines = desc.splitlines()
        
        # Extract additional info
        description = []
        additional_info = {}
        
        for line in lines:
            if not line:
                continue
            
            if ": " not in line or "Note: " in line:
                description.append(TextCleaner.clean_text(line))
            else:
                # Parse key-value pairs
                parts = line.split(": ")
                for i, part in enumerate(parts[:-1]):
                    if "subcultivation ratio" in part.lower():
                        value = parts[i + 1]
                        value = re.sub(r'Medium renewal', '', value, flags=re.IGNORECASE)
                        additional_info["Subcultivation ratio"] = TextCleaner.clean_text(value)
                    elif "medium renewal" in part.lower():
                        additional_info["Medium renewal"] = TextCleaner.clean_text(parts[i + 1])
        
        if description or steps:
            handling_info['Subculturing procedure'] = {
                'Description': " ".join(description) if description else None,
                'Procedure': steps if steps else None
            }
        
        handling_info.update(additional_info)
        return subculture_info


class ImageParser:
    """Parse and extract image URLs"""
    
    @staticmethod
    def extract_images(soup):
        """Extract image URLs and labels from page"""
        images = []
        image_elements = soup.find_all(class_=Config.Selectors.IMAGE_GALLERY)
        
        for element in image_elements:
            img_tag = element.find('img')
            if img_tag:
                link = Config.BASE_URL + img_tag.get("src")
                label = img_tag.get("alt")
                images.append((label, link))
        
        return images if images else None


class PriceParser:
    """Parse pricing information"""
    
    @staticmethod
    def extract_price(soup):
        """Extract price from product page"""
        price_element = soup.find('span', class_=Config.Selectors.PRICE_CURRENT)
        if not price_element:
            return None
        
        price_text = price_element.text.strip().replace("\xa0", " ")
        price_value = price_text.split(" ")[0][1:].replace(",", "")
        
        try:
            return float(price_value)
        except ValueError:
            return None
