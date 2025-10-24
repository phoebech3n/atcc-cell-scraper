## 📄 Data Output Format

### Overview

Each cell line is exported as a structured JSON object containing comprehensive protocol information. Data is available in two formats:

- **Individual files**: `data/cell_protocols/<cell_name>.json` (one file per cell)
- **Merged dataset**: `data/cell_protocols.json` (all cells in single file)

### Complete Example

Here's a real example from the ATCC CCL-81-VHG (Vero.STAT1 KO) cell line:

```json
{
  "Vero.STAT1 KO": {
    "ID": 2,
    "Cell Name": "Vero.STAT1 KO",
    "ATCC Number": "CCL-81-VHG",
    
    "Product category": "Animal cells",
    "Product type": ["Cell model"],
    "Product format": "Frozen",
    
    "Organism": "Cercopithecus aethiops",
    "Morphology": "epithelial",
    "Tissue": ["kidney"],
    "Disease": "Normal",
    
    "Applications": [
      "3D cell culture",
      "Vaccine development",
      "Bioproduction",
      "Cell and gene therapy (CGT) development"
    ],
    
    "Storage conditions": "Vapor phase of liquid nitrogen",
    "Unpacking and storage instructions": {
      "1": "Check all containers for leakage or breakage.",
      "2": "Remove the frozen cells from the dry ice packaging..."
    },
    
    "Complete medium": "The base medium for this cell line is ATCC-formulated Eagle's Minimum Essential Medium...",
    "Temperature": "37 degrees Celsius",
    "Atmosphere": [
        "95% Air", 
        "5% CO_2"
    ],

    "Handling procedure": {
      "Description": "To ensure the highest level of viability, thaw the vial and initiate...",
      "Procedure": {
        "1": "Thaw the vial by gentle agitation in a 37 degrees Celsius water bath...",
        "2": "Remove the vial from the water bath as soon as the contents are thawed...",
        "3": "Transfer the vial contents to a centrifuge tube...",
        "4": "Resuspend cell pellet with the recommended complete medium...",
        "5": "Incubate the culture at 37 degrees Celsius..."
      }
    },
    
    "Subculturing procedure": {
      "Description": "Volumes used in this protocol are for 75 cm^2 flask...",
      "Procedure": {
        "1": "Remove and discard culture medium.",
        "2": "Briefly rinse the cell layer with 0.25% (w/v) Trypsin...",
        "3": "Add 2.0 to 3.0 mL of Trypsin-EDTA solution to flask...",
        "4": "Add 6.0 to 8.0 mL of complete growth medium...",
        "5": "Add appropriate aliquots of the cell suspension...",
        "6": "Incubate cultures at 37 degrees Celsius."
      }
    },
    
    "Subcultivation ratio": "A subcultivation ratio of 1:3 to 1:6 is recommended",
    "Medium renewal": "2 to 3 times per week",
    "Reagents for cryopreservation": "Complete growth medium supplemented with 5% (v/v) DMSO",
    
    "Price": 5008.0,
    "ATCC Link": "https://www.atcc.org/products/ccl-81-vhg",
    "Images": null
  }
}
```

### Field Descriptions

#### Basic Information
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `ID` | integer | Unique identifier for the cell line | `2` |
| `Cell Name` | string | Official cell line name | `"Vero.STAT1 KO"` |
| `ATCC Number` | string | ATCC catalog number | `"CCL-81-VHG"` |
| `ATCC Link` | string | Direct URL to product page | `"https://www.atcc.org/products/..."` |

#### Classification
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Product category` | string | Broad category | `"Animal cells"` |
| `Product type` | array | Specific cell type(s) | `["Cell model"]` |
| `Product format` | string | Physical format | `"Frozen"` |
| `Organism` | string | Source organism (scientific name) | `"Cercopithecus aethiops"` |
| `Morphology` | string | Cell morphology | `"epithelial"` |
| `Tissue` | array | Tissue origin | `["kidney"]` |
| `Disease` | string | Disease state | `"Normal"` |

#### Applications & Use
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Applications` | array | Recommended applications | `["3D cell culture", "Vaccine development"]` |

#### Storage & Handling
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Storage conditions` | string | Long-term storage requirements | `"Vapor phase of liquid nitrogen"` |
| `Unpacking and storage instructions` | object | Numbered step-by-step instructions | `{"1": "Check all containers...", "2": "..."}` |

#### Culture Conditions
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Complete medium` | string | Medium composition details | `"ATCC-formulated Eagle's MEM + 10% FBS"` |
| `Temperature` | string | Incubation temperature | `"37 degrees Celsius"` |
| `Atmosphere` | array | Gas composition | `["95% Air", "5% CO_2"]` |

#### Procedures
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Handling procedure` | object | Initial thawing and setup protocol | `{"Description": "...", "Procedure": {...}}` |
| `Subculturing procedure` | object | Passaging protocol | `{"Description": "...", "Procedure": {...}}` |
| `Subcultivation ratio` | string | Recommended split ratio | `"1:3 to 1:6"` |
| `Medium renewal` | string | Medium change frequency | `"2 to 3 times per week"` |
| `Reagents for cryopreservation` | string | Freezing medium composition | `"Complete growth medium + 5% DMSO"` |

#### Pricing & Media
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Price` | float/null | Price in USD | `5008.0` |
| `Images` | array/null | Product images | `[["Label", "https://..."], ...]` or `null` |

### Data Quality Features

#### 1. **Unicode Normalization**
Some examples:
- Temperature symbols: `°C` → `"degrees Celsius"`
- Superscripts: `CO₂` → `"CO_2"`
- Special characters: `±` → `"plus/minus"`

#### 2. **Structured Procedures**
Procedures are parsed into numbered steps with both:
- **Description**: Context and important notes
- **Procedure**: Step-by-step instructions as numbered dictionary

Example:
```json
{
  "Description": "Volumes used in this protocol are for 75 cm^2 flask",
  "Procedure": {
    "1": "Remove and discard culture medium.",
    "2": "Briefly rinse the cell layer...",
    "3": "Add 2.0 to 3.0 mL of Trypsin-EDTA solution..."
  }
}
```

#### 3. **Consistent Data Types**
- **Strings**: Single-value text fields
- **Arrays**: Multiple values (tissues, applications, atmosphere)
- **Objects**: Nested structured data (procedures, instructions)
- **Numbers**: Prices, measurements
- **Null**: Missing/unavailable data

#### 4. **Clean Text**
- Removed ATCC product cross-references
- Normalized whitespace
- Sentence-level tokenization
- Preserved technical accuracy

### Common Field Combinations

#### Minimal Cell Entry (some fields may be null)
```json
{
  "ID": 1,
  "Cell Name": "Example Cell",
  "ATCC Number": "XXX-123",
  "ATCC Link": "https://...",
  "Price": 450.0
}
```

#### Complete Cell Entry (all available fields)
All fields shown in the complete example above, including detailed procedures, storage instructions, and culture conditions.

### Usage Examples

#### Load and Parse Data

```python
import json

# Load merged dataset
with open('cell_protocols.json', 'r') as f:
    cells = json.load(f)

# Access specific cell
vero_cell = cells['Vero.STAT1 KO']
print(f"Organism: {vero_cell['Organism']}")
print(f"Price: ${vero_cell['Price']}")

# Get handling steps
for step_num, instruction in vero_cell['Handling procedure']['Procedure'].items():
    print(f"Step {step_num}: {instruction}")
```

#### Filter by Criteria

```python
# Find cells from specific organism
human_cells = {
    name: data 
    for name, data in cells.items() 
    if data.get('Organism') == 'Homo sapiens'
}

# Find cells under $1000
affordable_cells = {
    name: data 
    for name, data in cells.items() 
    if data.get('Price') and data['Price'] < 1000
}

# Find cells for specific application
vaccine_cells = {
    name: data 
    for name, data in cells.items() 
    if 'Vaccine development' in data.get('Applications', [])
}
```

#### Extract Specific Information

```python
# Get all unique organisms
organisms = set(
    cell.get('Organism') 
    for cell in cells.values() 
    if cell.get('Organism')
)

# Get price statistics
prices = [cell['Price'] for cell in cells.values() if cell.get('Price')]
avg_price = sum(prices) / len(prices)
print(f"Average price: ${avg_price:.2f}")

# Count cells by tissue type
from collections import Counter
tissue_counts = Counter()
for cell in cells.values():
    for tissue in cell.get('Tissue', []):
        tissue_counts[tissue] += 1
```

### Data Statistics

Based on 1,000+ cell lines:

- **Average fields per cell**: 15-20 fields
- **Procedure steps**: Typically 4-6 steps for handling, 5-8 for subculturing
- **Price range**: $450 - $6,000+ USD
- **File size**: 
  - Individual files: 2-11 KB each
  - Merged dataset: ~4 MB total
- **Organisms**: 20+ species represented
- **Tissues**: 50+ tissue types

### Notes

- **Null values**: Indicate data not available on ATCC website
- **Empty arrays**: `[]` means field exists but no values provided
- **Procedure numbers**: Always strings (e.g., `"1"`, `"2"`) for consistent JSON parsing
- **Temperature format**: Always in Celsius with full text ("degrees Celsius")
- **Prices**: In USD, reflect pricing at time of scraping