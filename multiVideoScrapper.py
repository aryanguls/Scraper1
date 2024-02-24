import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def get_campaign_links(driver, base_url, page_number=1):
    url = f"{base_url}?page={page_number}" if page_number > 1 else base_url
    driver.get(url)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-span-1')))
    campaign_elements = driver.find_elements(By.CSS_SELECTOR, 'div.col-span-1 div.px-4 a[href^="/campaigns/"]')
    return [element.get_attribute('href') for element in campaign_elements]

def get_video_sources(driver, campaign_url):
    driver.get(campaign_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bg-white.my-3')))
    containers = driver.find_elements(By.CSS_SELECTOR, 'div.bg-white.my-3')
    video_sources = []
    for container in containers:
        iframe = container.find_elements(By.TAG_NAME, 'iframe')
        if iframe:
            video_sources.append(iframe[0].get_attribute('src'))
        video = container.find_elements(By.TAG_NAME, 'video')
        if video:
            video_sources.append(video[0].get_attribute('src'))
    return video_sources

if __name__ == "__main__":
    # User input for number of links or 'ALL' for all links
    user_input = input("Enter the number of links you want to scrape or type 'ALL' for all links: ").strip()
    max_links = None if user_input.upper() == 'ALL' else int(user_input)
    total_links_scraped = 0
    page_number = 1

    options = Options()
    options.page_load_strategy = 'normal'
    driver = webdriver.Chrome(options=options)
    base_url = 'https://www.adsoftheworld.com/campaigns'
    campaign_video_data = {}



    while True:
        campaign_links = get_campaign_links(driver, base_url, page_number)
        if not campaign_links or (max_links is not None and total_links_scraped >= max_links):
            break
        print(f"Processing page {page_number} with {len(campaign_links)} campaigns")
        
        for link in campaign_links:
            if max_links is not None and total_links_scraped >= max_links:
                break
            video_sources = get_video_sources(driver, link)
            campaign_video_data[link] = video_sources
            total_links_scraped += 1
        
        page_number += 1

    driver.quit()
    
    # Write the campaign and video links data to a JSON file
    with open('video_data.json', 'w') as file:
        json.dump(campaign_video_data, file, indent=4)

    print(f"Data for {total_links_scraped} campaigns has been written to video_data.json")
