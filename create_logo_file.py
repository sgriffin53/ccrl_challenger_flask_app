html_file = 'engine_logos_html.htm'
from bs4 import BeautifulSoup
import re


def extract_engine_name(full_name):
    """
    Extracts the engine name (the first word before any numbers or additional descriptors)
    from a given string.

    Args:
        full_name (str): The full engine description, e.g., 'Stockfish 17 64-bit 8CPU'.

    Returns:
        str: The extracted engine name, e.g., 'Stockfish'.
    """
    match = re.match(r'^([A-Za-z]+)', full_name)
    return match.group(1) if match else None

def extract_chess_engines(html):
    """
    Extract chess engine names and their associated image URLs from the given HTML input.

    Args:
        html (str): The HTML input containing <img> tags with chess engine images.

    Returns:
        dict: A dictionary where keys are chess engine names and values are their image URLs.
    """
    soup = BeautifulSoup(html, 'html.parser')
    engines = {}

    for img_tag in soup.find_all('img'):
        img_url = img_tag.get('src')
        alt_text = img_tag.get('alt')

        if img_url and alt_text:
            # Extract the engine name from the image URL if it matches the pattern
            engine_name = img_url.split('/')[-1].split('.')[0]
            engine_name = engine_name.replace("-"," ")
            engine_name = engine_name.replace("CM11th_","")
            #engine_name = engine_name.remove("CM10")
            engines[engine_name] = img_url

    return engines

def create_logo_file(logo_dict):
    f = open('logo_urls.txt', 'w', encoding='utf-8')
    for key in logo_dict.keys():
        f.write(key + "|" + logo_dict[key] + "\n")
    f.close()


def get_engine_logo(engine_name, logo_dict):
    engine_name = extract_engine_name(engine_name)
    if engine_name not in logo_dict: return None
    return logo_dict[engine_name]

f = open(html_file, 'r', encoding='utf-8')
lines = f.readlines()
f.close()
html = ''
for line in lines:
   # print(line)
    html += line
logo_dict = extract_chess_engines(html)
create_logo_file(logo_dict)