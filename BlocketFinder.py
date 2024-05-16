from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_driver():
    options = Options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def get_data(driver, url):
    driver.get(url)
    time.sleep(3)  # Wait for the page to fully load
    return driver.page_source

def filter_data(page_source, file):
    soup = BeautifulSoup(page_source, 'html.parser')
    
    unwanted_labels = {
        "Spara annons som favorit", "Gå till huvudsidan", "Vad vill du söka efter?", 
        "Sök", "Skapa bevakning", "Sökfilter", "Alla filter", "Kategori", "Plats", 
        "Pris", "Annonser med frakt", "Typ av annonsör", "Aktiva sökfilter", 
        "Privat, klicka för att ta bort", "Skapa bevakning", "Luleå, klicka för att ta bort"
    }
    
    # Find all elements with the aria-label attribute, excluding the information in unwanted_labels
    ItemTitle = [item for item in soup.find_all(attrs={"aria-label": True}) if item["aria-label"] not in unwanted_labels]  
      
    TimeData = soup.find_all('p', class_='styled__Time-sc-1kpvi4z-18 jMeTyX')
    
    ItemPrice = soup.find_all('div', class_='Price__StyledPrice-sc-1v2maoc-1 lbJRcp')
    
    ItemLink = soup.find_all('a', class_='Link-sc-6wulv7-0 styled__StyledTitleLink-sc-1kpvi4z-8 kDBOOn jVZtER')

    # Iterate over each item and print its details
    for link, price, data, title in zip(ItemLink, ItemPrice, TimeData, ItemTitle):
        item_details = (
            f"Title: {title['aria-label']}\n"
            f"Price: {price.text}\n"
            f"Time: {data.text}\n"
            f"Link: {baserurl + link['href']}\n"
            "--------------------------\n"
            "\n"
        )
        # print(item_details)
        file.write(item_details)

def scrape_all_pages(start_url, base_url, max_pages=None):
    driver = get_driver()
    page_number = 1

    with open("scraped_data.txt", "w", encoding="utf-8") as file:
        try:
            while True:
                current_url = f"{start_url}&page={page_number}"
                page_source = get_data(driver, current_url)
                filter_data(page_source, file)
                
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

url = "https://www.blocket.se/annonser/norrbotten?r=1&m=9&f=p"
baserurl = "https://www.blocket.se"

scrape_all_pages(url, baserurl)  # Remove max_pages or set it as needed
# scrape_all_pages(url, baserurl max_pages=5)