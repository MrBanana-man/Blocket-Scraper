from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys
import subprocess

def get_driver():
    options = Options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def get_data(driver, url):
    driver.get(url)
    time.sleep(3)  # Wait for the page to fully load
    return driver.page_source

def filter_data(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    
    unwanted_labels = {
        "Spara annons som favorit", "Gå till huvudsidan", "Vad vill du söka efter?", 
        "Sök", "Skapa bevakning", "Sökfilter", "Alla filter", "Kategori", "Plats", 
        "Pris", "Annonser med frakt", "Typ av annonsör", "Aktiva sökfilter", 
        "Privat, klicka för att ta bort", "Skapa bevakning", "Luleå, klicka för att ta bort", "Breadcrumb", 
        "Sök inom Elektronik", "Typ av säljare", "Elektronik, klicka för att ta bort", "list-icon-filled", "grid-icon"
    }
    
    # Find all elements with the aria-label attribute, excluding the information in unwanted_labels
    ItemTitle = [item for item in soup.find_all(attrs={"aria-label": True}) if item["aria-label"] not in unwanted_labels]  
      
    TimeData = soup.find_all('p', class_='styled__Time-sc-1kpvi4z-18 jMeTyX')
    
    ItemPrice = soup.find_all('div', class_='Price__StyledPrice-sc-1v2maoc-1 lbJRcp')
    
    ItemLink = soup.find_all('a', class_='Link-sc-6wulv7-0 styled__StyledTitleLink-sc-1kpvi4z-8 kDBOOn jVZtER')

    # Create lists to store the data
    titles = []
    prices = []
    times = []
    links = []
    
    # Iterate over each item and collect its details
    for link, price, data, title in zip(ItemLink, ItemPrice, TimeData, ItemTitle):
        input_title = title['aria-label']
        input_title_array = input_title.splitlines()
        
        titles.append(input_title_array[0])
        prices.append(price.text.strip())
        times.append(data.text.strip())
        links.append(baserurl + link['href'])

    return titles, prices, times, links

def scrape_pages(start_url, base_url, max_pages=None):
    driver = get_driver()
    page_number = 1

    all_titles = []
    all_prices = []
    all_times = []
    all_links = []

    try:
        while True:
            current_url = f"{start_url}&page={page_number}"
            page_source = get_data(driver, current_url)
            titles, prices, times, links = filter_data(page_source)
            
            all_titles.extend(titles)
            all_prices.extend(prices)
            all_times.extend(times)
            all_links.extend(links)
            
            # Optionally stop after a certain number of pages
            if max_pages and page_number >= max_pages:
                break
            
            # Check if there's a next page (optional stop condition)
            soup = BeautifulSoup(page_source, 'html.parser')
            next_page_button = soup.find('a', class_='Pagination__Button-sc-uamu6s-1 Pagination__PrevNextButton-sc-uamu6s-7 ixEXJs faPyAe')
            if not next_page_button:
                print("NO MORE PAGES TO SCRAPE")
                break
            
            page_number += 1
    finally:
        driver.quit()

    # Create a DataFrame
    df = pd.DataFrame({
        'Title': all_titles,
        'Price': all_prices,
        'Time': all_times,
        'Link': all_links
    })

    # Save the DataFrame to a CSV file
    df.to_csv('scraped_data.csv', index=False, encoding='utf-8')

url = "https://www.blocket.se/annonser/norrbotten/elektronik?cg=5000&r=1&m=9&f=p"
baserurl = "https://www.blocket.se"

scrape_pages(url, baserurl, max_pages=1)  # Remove max_pages or set it as needed
print("Done scraping")
subprocess.call([sys.executable, r"PYTHON\Projects\BlocketFinder\DBsorter.py"])