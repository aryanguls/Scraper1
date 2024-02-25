import json
import subprocess
import requests
from pytube import YouTube
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import os

def download_youtube_video(video_url, save_path):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
        if stream:
            filename = stream.download(save_path)
            print(f"Video downloaded: {filename}")
            return os.path.join(save_path, stream.default_filename)
    except Exception as e:
        print(f"Failed to download video: {e}")
    return None
    
def download_vimeo_video(video_url, save_path):
    filename = video_url.split("/")[-1] + ".mp4"  # Simple filename based on URL
    full_path = os.path.join(save_path, filename)
    command = ['yt-dlp', video_url, '-o', full_path]
    try:
        result = subprocess.run(command, capture_output=True, check=True)
        print("Video downloaded successfully:", result.stdout)
        return full_path
    except subprocess.CalledProcessError as e:
        print("Error downloading video:", e)
        return None

def download_mp4_video(video_url, save_path):
    try:
        filename = video_url.split("/")[-1]
        full_path = os.path.join(save_path, filename)
        response = requests.get(video_url, stream=True)
        with open(full_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Video downloaded: {full_path}")
        return full_path
    except Exception as e:
        print(f"Failed to download video: {e}")
        return None
        
def load_page_with_retry(driver, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            driver.get(url)
            return True  # Page loaded successfully
        except TimeoutException:
            print(f"Timeout loading page {url}, retrying {attempt + 1}/{max_retries}...")
    return False  # Failed to load page after retries

def get_campaign_links(driver, base_url, page_number=1, max_links=None):
    url = f"{base_url}?page={page_number}" if page_number > 1 else base_url
    if not load_page_with_retry(driver, url):
        print(f"Failed to load {url} after retries. Skipping page {page_number}...")
        return []
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-span-1')))
    campaign_elements = driver.find_elements(By.CSS_SELECTOR, 'div.col-span-1 div.px-4 a[href^="/campaigns/"]')
    campaign_links = [element.get_attribute('href') for element in campaign_elements]
    return campaign_links[:max_links] if max_links else campaign_links

def get_video_sources_and_metadata(driver, campaign_url, save_path):
    if not load_page_with_retry(driver, campaign_url):
        print(f"Failed to load {campaign_url} after retries. Skipping...")
        return None
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bg-white.my-3')))
    
    title_element = driver.find_elements(By.CSS_SELECTOR, 'h1.text-2xl.opensanssemibold')
    title = title_element[0].text if title_element else "Unknown Title"
    
    agency_element = driver.find_elements(By.CSS_SELECTOR, 'p.mt-4 a[href^="/agencies/"]')
    agency_name = agency_element[0].text if agency_element else "Unknown Agency"
    agency_link = agency_element[0].get_attribute('href') if agency_element else None
    
    brand_element = driver.find_elements(By.CSS_SELECTOR, 'p > span > a[href^="/brands/"]')
    brand_name = brand_element[0].text if brand_element else "Unknown Brand"
    brand_link = brand_element[0].get_attribute('href') if brand_element else None

    # Extract categories
    categories_elements = driver.find_elements(By.CSS_SELECTOR, 'div.categories a')
    categories = [element.text for element in categories_elements]

    containers = driver.find_elements(By.CSS_SELECTOR, 'div.bg-white.my-3')

    video_data = [] 

    for container in containers:
        video_source = None
        download_path = None
        iframe = container.find_elements(By.TAG_NAME, 'iframe')
        video = container.find_elements(By.TAG_NAME, 'video')
        
        if iframe:
            video_source = iframe[0].get_attribute('src')
            if "youtube" in video_source or "youtu.be" in video_source:
                download_path = download_youtube_video(video_source, save_path)
            elif "vimeo" in video_source:
                download_path = download_vimeo_video(video_source, save_path)
        elif video:
            video_source = video[0].get_attribute('src')
            if "adsoftheworld" in video_source:
                download_path = download_mp4_video(video_source, save_path)
        
        if video_source:
            video_data.append({'video_link': video_source, 'download_path': download_path})
        

    
    return {
        'campaign_link': campaign_url,
        'title': title,
        'agency': {
            'name': agency_name,
            'link': agency_link
        },
        'brand': {
            'name': brand_name,
            'link': brand_link
        },
        'categories': categories,
        'videos': video_data
    }

if __name__ == "__main__":
    user_input = input("Enter the number of links you want to scrape or type 'ALL' for all links: ").strip()
    max_links = None if user_input.upper() == 'ALL' else int(user_input)
    options = Options()
    options.page_load_strategy = 'normal'
    driver = webdriver.Chrome(options=options)
    base_url = 'https://www.adsoftheworld.com/campaigns'
    campaign_video_data = []
    page_number = 1
    links_scraped = 0
    save_path = "AdsOfTheWorld"

    while True:
        campaign_links = get_campaign_links(driver, base_url, page_number, max_links - links_scraped if max_links else None)
        if not campaign_links or (max_links is not None and links_scraped >= max_links):
            break
        for link in campaign_links:
            campaign_data = get_video_sources_and_metadata(driver, link, save_path)
            if campaign_data:  # Check if campaign_data is not None
                campaign_video_data.append(campaign_data)
                links_scraped += 1
                # Write/update JSON file after each campaign is processed
                with open('video_data.json', 'w') as file:
                    json.dump(campaign_video_data, file, indent=4)
            if max_links is not None and links_scraped >= max_links:
                break
        if max_links is not None and links_scraped >= max_links:
            break
        page_number += 1

    driver.quit()

    print(f"Data for {links_scraped} campaigns has been written to video_data.json")

