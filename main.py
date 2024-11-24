import requests
from bs4 import BeautifulSoup
import csv
import time

# Function to get listings from a single page
def get_listings(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(class_='rows')
    if results:
        return results.find_all('li', class_='result-row')
    return []

# Function to parse the details of a particular listing
def get_listing_details(listing_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    page = requests.get(listing_url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    # Extract attributes and description
    attributes = soup.find_all('p', class_='attrgroup')
    details = []
    for attribute in attributes:
        spans = attribute.find_all('span')
        details.extend([span.text.strip() for span in spans])
    
    description = soup.find('section', {"id": "postingbody"})
    description_text = description.text.strip() if description else "No description available"
    
    return details, description_text

# Base URL for Craigslist Toronto with a search query for commercial kitchens
BASE_URL = 'https://toronto.craigslist.org/search/sss?query=commercial+kitchen'

# File to save the results
OUTPUT_FILE = 'toronto_kitchen_rentals.csv'

# Open CSV file for writing
with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['title', 'price', 'location', 'url', 'details', 'description']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Loop through multiple pages
    for page_offset in range(0, 300, 120):  # Pagination increments by 120
        search_url = f"{BASE_URL}&s={page_offset}"
        print(f"Scraping page: {search_url}")
        
        # Get listings from the current page
        listings = get_listings(search_url)
        if not listings:
            print("No more listings found.")
            break
        
        for listing in listings:
            title_elem = listing.find('a', class_='result-title hdrlnk')
            price_elem = listing.find('span', class_='result-price')
            location_elem = listing.find('span', class_='result-hood')
            url_elem = listing.find('a', class_='result-title hdrlnk')['href']

            title = title_elem.text.strip() if title_elem else 'No title'
            price = price_elem.text.strip() if price_elem else 'No price'
            location = location_elem.text.strip() if location_elem else 'No location'
            url = url_elem

            # Get details and description from the specific listing
            details, description = get_listing_details(url)
            
            # Write the data to CSV
            writer.writerow({
                'title': title,
                'price': price,
                'location': location,
                'url': url,
                'details': ", ".join(details),
                'description': description
            })
        
        # Be polite and avoid overwhelming the server
        time.sleep(2)

print(f"Scraping completed. Data saved to {OUTPUT_FILE}.")