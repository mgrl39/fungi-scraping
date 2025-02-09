import requests
from bs4 import BeautifulSoup
import json
import os
import re
import signal
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

# Enhanced color class
class Colors:
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    YELLOW = Fore.YELLOW
    GREEN = Fore.GREEN
    RED = Fore.RED
    BLUE = Fore.BLUE
    WHITE = Fore.WHITE
    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL
    BG_BLACK = Back.BLACK

def signal_handler(signum, frame):
    print(f"\n{Colors.YELLOW}Received interrupt signal. Stopping...{Colors.RESET}")
    exit()

# Set up the signal handler
signal.signal(signal.SIGINT, signal_handler)


def print_logo():
    logo = f"""
                                    ████   ████████   ████████
                                   ░░███  ███░░░░███ ███░░░░███
 █████████████    ███████ ████████  ░███ ░░░    ░███░███   ░███
░░███░░███░░███  ███░░███░░███░░███ ░███    ██████░ ░░█████████
 ░███ ░███ ░███ ░███ ░███ ░███ ░░░  ░███   ░░░░░░███ ░░░░░░░███
 ░███ ░███ ░███ ░███ ░███ ░███      ░███  ███   ░███ ███   ░███
 █████░███ █████░░███████ █████     █████░░████████ ░░████████
░░░░░ ░░░ ░░░░░  ░░░░░███░░░░░     ░░░░░  ░░░░░░░░   ░░░░░░░░
                 ███ ░███
                ░░██████
                 ░░░░░░
"""
    print(f"{Colors.CYAN}{Colors.BOLD}{logo}{Colors.RESET}")

def print_text(name, text):
    name_color = f"{Colors.YELLOW}{Colors.BOLD}"
    text_color = Colors.WHITE if text else f"{Colors.RED}"
    print(f"{name_color}{name}:{Colors.RESET} {text_color}{text if text else 'NULL'}{Colors.RESET}")

def print_section(title):
    print(f"\n{Colors.GREEN}{Colors.BOLD}{'=' * 50}")
    print(f"{Colors.BLUE}{Colors.BOLD}{title.center(50)}")
    print(f"{Colors.GREEN}{Colors.BOLD}{'=' * 50}{Colors.RESET}\n")

def format_name(name):
    return name.strip().lower().replace(' ', '-')

def get_text_or_none(soup_element):
    return soup_element.text.strip() if soup_element else None

def scrape_fungi_details(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"{Colors.RED}Error accessing {url}{Colors.RESET}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Title and Author
        title = get_text_or_none(soup.select_one('h3.itemTitle'))
        author = get_text_or_none(soup.select_one('span.itemAuthor'))

        # Additional Information (including "Common name" and "Synonym")
        additional_info = {}
        additional_info_section = soup.find('div', class_='itemExtraFieldsFungi')
        if additional_info_section:
            for li in additional_info_section.find_all('li', class_='caracteristica'):
                label = li.find('span', class_='itemExtraFieldsLabel')
                value = li.find('span', class_='itemExtraFieldsValue')
                if label and value:
                    key = label.text.strip().strip(':')
                    val = value.text.strip()
                    additional_info[key] = val

        common_name = additional_info.get("Nombre común")
        synonym = additional_info.get("Sinónimo")

        # Taxonomy (excluding "Common name" and "Synonym")
        taxonomy_section = soup.find('div', class_='taxonomia')
        taxonomy = {}
        if taxonomy_section:
            for li in taxonomy_section.find_all('li', class_='caracteristica'):
                label = li.find('span', class_='itemExtraFieldsLabel')
                value = li.find('span', class_='itemExtraFieldsValue')
                if label and value:
                    key = label.text.strip().strip(':')
                    val = value.text.strip()
                    if key not in ["Nombre común", "Sinónimo"]:
                        taxonomy[key] = val

        # Edibility
        edibility = None
        edibility_img = soup.select_one('div.itemToolbarFungi img')
        if edibility_img:
            match = re.search(r'/images/comestibilidad/(.*?).png', edibility_img['src'])
            if match:
                edibility = match.group(1)

        # Characteristics, Habitat, and Observations
        characteristics = {}
        habitat, observations = None, None

        full_text = soup.select_one('div.itemFullText')
        if full_text:
            h3_headers = full_text.find_all('h3')
            paragraphs = full_text.find_all('p')
            current_section = None

            for header in h3_headers:
                if "Características" in header.text:
                    current_section = "characteristics"
                elif "Hábitat" in header.text:
                    current_section = "habitat"
                elif "Observaciones" in header.text:
                    current_section = "observations"

                if current_section == "characteristics":
                    characteristics["cap"] = paragraphs[0].text.strip() if len(paragraphs) > 0 else None
                    characteristics["hymenium"] = paragraphs[1].text.strip() if len(paragraphs) > 1 else None
                    characteristics["stipe"] = paragraphs[2].text.strip() if len(paragraphs) > 2 else None
                    characteristics["flesh"] = paragraphs[3].text.strip() if len(paragraphs) > 3 else None
                elif current_section == "habitat":
                    habitat = paragraphs[4].text.strip() if len(paragraphs) > 4 else None
                elif current_section == "observations":
                    observations = paragraphs[5].text.strip() if len(paragraphs) > 5 else None

        # Structured data
        data = {
            "name": url.split('/')[-1].replace('.html', ''),
            "title": title,
            "author": author,
            "additional_info": {
                "common_name": common_name,
                "synonym": synonym,
            },
            "taxonomy": taxonomy,
            "edibility": edibility,
            "characteristics": characteristics,
            "habitat": habitat,
            "observations": observations,
        }

        return data
    except Exception as e:
        print(f"{Colors.RED}Error processing {url}: {e}{Colors.RESET}")
        return None

def scrape_fungi_names(base_url, max_offset):
    names = []
    for offset in range(0, max_offset + 1, 20):
        print(f'{Colors.YELLOW}Scraping page with offset {offset}{Colors.RESET}')
        page_url = f"{base_url}?start={offset}"
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.select('h3.catItemTitle')
        for headline in headlines:
            name = headline.text.strip()
            names.append(name)
            print(f'{Colors.GREEN}Added: {name}{Colors.RESET}')
    return names

def count_fungi(names):
    return len(names)

def display_warning(count):
    print(f"\n{Colors.RED}{Colors.BOLD}WARNING:{Colors.RESET}")
    print(f"{Colors.YELLOW}This script will scrape {Colors.BOLD}{count}{Colors.RESET}{Colors.YELLOW} fungi from Fungipedia.{Colors.RESET}")
    print(f"{Colors.YELLOW}Do you want to continue? {Colors.BOLD}(y/N){Colors.RESET}")
    response = input().strip().lower()
    return response == 'y'

def display_menu():
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}")
    print(f"{Colors.MAGENTA}{'FUNGI SCRAPER MENU'.center(50)}")
    print(f"{Colors.CYAN}{'=' * 50}{Colors.RESET}\n")
    print(f"{Colors.YELLOW}1. {Colors.WHITE}Scrape fungi names from website")
    print(f"{Colors.YELLOW}2. {Colors.WHITE}Use existing names.txt file")
    print(f"{Colors.YELLOW}0. {Colors.WHITE}Exit")
    print(f"\n{Colors.CYAN}{'=' * 50}{Colors.RESET}")

def main():
    print_logo()
    display_menu()
    choice = input(f"{Colors.GREEN}Enter your choice (1 or 2): {Colors.RESET}")

    if choice == '1':
        base_url = "https://www.fungipedia.org/hongos.html"
        max_offset = 560  # Change this if there are more pages in the future
        print_section("Scraping Fungi Names")
        fungi_names = scrape_fungi_names(base_url, max_offset)
        
        # Save scraped names to names.txt
        with open('names.txt', 'w', encoding='utf-8') as file:
            for name in fungi_names:
                file.write(f"{name}\n")
        print(f"{Colors.GREEN}Scraped names saved to names.txt{Colors.RESET}")
    elif choice == '2':
        if not os.path.exists('names.txt'):
            print(f"{Colors.RED}Error: names.txt file not found.{Colors.RESET}")
            return
        with open('names.txt', 'r', encoding='utf-8') as file:
            fungi_names = [line.strip() for line in file.readlines()]
        print(f"{Colors.GREEN}Names loaded from names.txt{Colors.RESET}")
    elif choice == '0':
        print(f"{Colors.YELLOW}Exiting.{Colors.RESET}")
        exit()
    else:
        print(f"{Colors.RED}Invalid choice. Exiting.{Colors.RESET}")
        return

    fungi_count = count_fungi(fungi_names)
    if not display_warning(fungi_count):
        print(f"{Colors.RED}Scraping cancelled.{Colors.RESET}")
        return

    base_url = "https://www.fungipedia.org/hongos/"
    os.makedirs('output_jsons', exist_ok=True)

    for i, name in enumerate(fungi_names, 1):
        print_section(f"Processing: {name} ({i}/{fungi_count})")
        formatted_name = format_name(name)
        url = f"{base_url}{formatted_name}.html"
        print_text("URL", url)

        fungi_details = scrape_fungi_details(url)
        if fungi_details:
            json_filename = f'output_jsons/{formatted_name}.json'
            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json.dump(fungi_details, json_file, ensure_ascii=False, indent=4)
            print(f"{Colors.GREEN}Save to {json_filename}{Colors.RESET}")

    print_section("Scraping Completed")
    print(f"{Colors.CYAN}{Colors.BOLD}JSON files generated for scraped fungi.{Colors.RESET}")

if __name__ == "__main__":
    main()
