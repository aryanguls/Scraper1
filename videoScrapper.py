import os
from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize the Selenium WebDriver (Assuming Chrome here, and chromedriver needs to be in PATH)
driver = webdriver.Chrome()

# Open the URL (replace 'https://www.example.com' with the actual URL you want to scrape)
driver.get('https://www.adsoftheworld.com/campaigns/the-old-man')

# Wait for the page to load (can be replaced with more sophisticated WebDriverWait)
driver.implicitly_wait(10)

# Look for the common div container for both video types
containers = driver.find_elements(By.CSS_SELECTOR, 'div.bg-white.my-3')

# Initialize a list to hold the video sources
video_sources = []

# Iterate through the containers to find iframe or video tags
for container in containers:
    # Try to find an iframe tag
    iframe = container.find_elements(By.TAG_NAME, 'iframe')
    if iframe:
        video_sources.append(iframe[0].get_attribute('src'))
    
    # Try to find a video tag
    video = container.find_elements(By.TAG_NAME, 'video')
    if video:
        video_sources.append(video[0].get_attribute('src'))

# Close the driver after the operation is complete
driver.quit()

# Print the extracted video sources
for src in video_sources:
    print(src)
