import os
import re
from typing import List, Dict, Any


def parse_menu_file(file_path: str) -> List[Dict[str, Any]]:
    """Parses a markdown menu file and extracts items based on common patterns."""
    items = []
    filename = os.path.basename(file_path)
    category_raw = filename.replace('Bella Terra ', '').replace(' Menu.md', '').replace(' List.md', '')
    category = category_raw.lower().replace(' ', '_')

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split content into potential item blocks
    # This regex looks for a number followed by a dot and then a bolded name
    # It captures the block until the next similar pattern or end of file
    item_blocks = re.split(r'\n\s*\d+\.\s*\*\*(.*?)\*\*\s*\n', content)
    
    # The first element is usually empty or header before the first item
    if len(item_blocks) > 1:
        # The split pattern captures the name, so we need to pair them up
        # item_blocks[0] is pre-content, then item_blocks[1] is name, item_blocks[2] is content, etc.
        parsed_blocks = []
        for i in range(1, len(item_blocks), 2):
            if i + 1 < len(item_blocks):
                parsed_blocks.append({
                    "name": item_blocks[i].strip(),
                    "content": item_blocks[i+1].strip()
                })

        for block in parsed_blocks:
            name = block["name"]
            item_content = block["content"]
            description = ""
            price = 0.0
            is_vegetarian = False
            is_vegan = False
            is_gluten_free = False
            properties = {}

            # Extract price
            price_match = re.search(r'_Price:_\s*£([\d\.]+)', item_content)
            if price_match:
                price = float(price_match.group(1))
            else:
                # Try to find price without explicit '_Price:' label (e.g., Pizza menu)
                price_match = re.search(r'£([\d\.]+)', item_content)
                if price_match:
                    price = float(price_match.group(1))

            # Extract description (everything after price/type/region until next item or end)
            desc_match = re.search(r'_Description:_\s*(.*?)(?:\n\n|\Z)', item_content, re.DOTALL)
            if desc_match:
                description = desc_match.group(1).strip()
            else:
                # Fallback for description if no explicit label
                # Capture content after name and properties until next item or end
                lines = item_content.split('\n')
                desc_lines = []
                in_description = False
                for line in lines:
                    if line.strip().startswith(('_Type:', '_Region:', '_Grape:', '_Price:')):
                        in_description = True # Start capturing after properties
                        continue
                    if in_description or not line.strip(): # Capture empty lines too if in description mode
                        desc_lines.append(line.strip())
                description = ' '.join(desc_lines).strip()

            # Extract properties (Type, Region, Grape, etc.)
            type_match = re.search(r'_Type:_\s*(.*?)(?:\n|_Price:|_Description:|$)', item_content)
            if type_match: properties["type"] = type_match.group(1).strip()
            region_match = re.search(r'_Region:_\s*(.*?)(?:\n|_Price:|_Description:|$)', item_content)
            if region_match: properties["region"] = region_match.group(1).strip()
            grape_match = re.search(r'_Grape:_\s*(.*?)(?:\n|_Price:|_Description:|$)', item_content)
            if grape_match: properties["grape"] = grape_match.group(1).strip()

            # Dietary flags (common in Pizza/Pasta/Lunch)
            if re.search(r'vegetarian', item_content, re.IGNORECASE): is_vegetarian = True
            if re.search(r'vegan', item_content, re.IGNORECASE): is_vegan = True
            if re.search(r'gluten-free', item_content, re.IGNORECASE): is_gluten_free = True
            
            # Special handling for Pizza menu descriptions which are often just the ingredients
            if category == "pizza_menu":
                # For pizzas, the description is often just the text after the name and before the price
                # Let's refine this to capture the actual description/ingredients
                pizza_desc_match = re.search(r'\*\*.*?\*\*\s*\n(.*?)(?:\n_Price:|_Price:|$)', item_content, re.DOTALL)
                if pizza_desc_match:
                    description = pizza_desc_match.group(1).strip()

            items.append({
                "name": name,
                "description": description,
                "price": price,
                "category": category,
                "is_vegetarian": is_vegetarian,
                "is_vegan": is_vegan,
                "is_gluten_free": is_gluten_free,
                "properties": properties
            })
    return items


def parse_all_menu_files(menu_dir: str) -> List[Dict[str, Any]]:
    """Parse all menu files in the specified directory."""
    all_items = []
    for filename in os.listdir(menu_dir):
        if filename.endswith(".md") and "about_us" not in filename:
            file_path = os.path.join(menu_dir, filename)
            print(f"Parsing {file_path}...")
            parsed_items = parse_menu_file(file_path)
            all_items.extend(parsed_items)
    return all_items 