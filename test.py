from selenium import webdriver
from selenium.webdriver.common.by import By
import concurrent.futures
import time
driver=webdriver.Chrome()

# Initialize the driver
links=[
    'https://google.com',
    'https://google.com',
    'https://google.com',
    'https://google.com'
]

driver.get(links[0])
# Function to open a link in a new tab
def open_link_in_new_instance(link):
    driver.switch_to.new_window('tab')
    driver.get(link)


# Use concurrent.futures to open the remaining links in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Start the remaining links in new tabs
    executor.map(open_link_in_new_instance, links[1:])

# Give time to view the opened tabs
time.sleep(10)

