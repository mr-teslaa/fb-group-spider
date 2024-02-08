import os
import time
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# KEYWORDS YOU WANT TO SEARCH
search_keyword = 'youtube promotion'

# xpaths
group_details_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "xk50ysn", " " )) and contains(concat( " ", @class, " " ), concat( " ", "x17z8epw", " " ))] | //*[contains(concat( " ", @class, " " ), concat( " ", "x1yc453h", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "xk50ysn", " " ))]'
members_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "xt0b8zv", " " )) and contains(concat( " ", @class, " " ), concat( " ", "xi81zsa", " " ))]'

# configure driver
service = Service(executable_path='C:/Hossain Foysal/Software/chromedriver-win64/chromedriver.exe')
options = webdriver.ChromeOptions()
prefs = {
    "profile.default_content_setting_values.notifications" : 2
}
options.add_experimental_option("prefs",prefs)
options.add_argument("--start-maximized")

# specify the path to chromedriver.exe (download and save on your computer)
driver = webdriver.Chrome(service=service, options=options)

# OPEN THE WEBSITE
driver.get("https://facebook.com")

###################################
# START - LOGIN - enter login credential
###################################


# GET THE INPUT FILEDS OF EMAIL AND PASSWORD
# WE NEED IT BECAUSE WE NEED TO TELL THE SELENIUM WHICH INPUT FIELD WE NEED TO TYPING
username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))

# TYPING USERNAME AND PASSWORD
username.clear()
username.send_keys(os.getenv('FB_USERNAME'))
password.clear()
password.send_keys(os.getenv('FB_PASSWORD'))

#target the login button and click it
button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

#wait 5 seconds to allow your new page to load
time.sleep(2)
###################################
# END - LOGIN
###################################


###################################
# START - SEARCH BAR - go to search bar and type the keyword
###################################
# go to the groups with keywords
group_search_url = f"https://www.facebook.com/search/groups?q={search_keyword}"
driver.get(group_search_url)
time.sleep(5)
###################################
# START - SEARCH BAR
###################################


#scroll down
#increase the range to sroll more
for j in range(0,2):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

# Function to clean and extract group links
def extract_clean_group_links(anchors):
    clean_group_links = []
    for a in anchors:
        if a.startswith("https://www.facebook.com/groups"):
            parsed_url = urlparse(a)
            clean_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
            if clean_url == 'https://www.facebook.com/groups/':
                continue
            clean_group_links.append(clean_url)
    
    # Remove duplicate links
    clean_group_links = list(set(clean_group_links))
    return clean_group_links

# Function to get group details
def get_group_details(driver, group_details_xpath):
    
    # Find the elements matching the XPath
    group_details_elements = driver.find_elements(By.XPATH, group_details_xpath)

    # Store the group details in a dictionary
    group_details = {}

    for element in group_details_elements:
        get_group_name = driver.find_element(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "xt0b8zv", " " )) and contains(concat( " ", @class, " " ), concat( " ", "x1xlr1w8", " " ))]')
        group_details["Group Name"] = get_group_name.text.strip()

        text = element.text.strip()
        if text:
            # Check the text content and store accordingly
            if "Public" in text or "Private" in text:
                group_details["Group Status"] = text
            elif "Visible" in text or "Hidden" in text:
                group_details["Visible Status"] = text
            elif "History" in text or "Tags" in text:
                pass
            else:
                group_details["Location"] = text
    return group_details


anchors = driver.find_elements(By.TAG_NAME, 'a')
anchors = [a.get_attribute('href') for a in anchors]

clean_group_links = extract_clean_group_links(anchors)

# Loop through the group URLs
for group_url in clean_group_links:
    # Visit the group URL for about section
    group_url_about = group_url + 'about/' 
    driver.get(group_url_about)
    
    # Get group details from the about section
    group_details_about = get_group_details(driver, group_details_xpath)

    # Get the number of group members
    group_members_element = driver.find_element(By.XPATH, members_xpath)
    number_of_members = group_members_element.text.strip()
    
    # Add the number of members to the group details obtained from the about section
    group_details_about["Members"] = number_of_members
    
    # Print the combined group details
    print("Group Name:", group_details_about.get("Group Name", "Not available"))
    print("Group URL:", group_url)
    print("Group Status:", group_details_about.get("Group Status", "Not available"))
    print("Visible Status:", group_details_about.get("Visible Status", "Not available"))
    print("Location:", group_details_about.get("Location", "Not available"))
    print("Number of Members:", number_of_members)
    print("-" * 20)  # Separator between groups