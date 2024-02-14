import os
import time
import pandas as pd
from slugify import slugify
from urllib.parse import urlparse 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from dotenv import find_dotenv, load_dotenv
from datetime import datetime, timedelta

load_dotenv(find_dotenv())

########################################
# xpaths
########################################
group_details_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "xk50ysn", " " )) and contains(concat( " ", @class, " " ), concat( " ", "x17z8epw", " " ))] | //*[contains(concat( " ", @class, " " ), concat( " ", "x1yc453h", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "xk50ysn", " " ))]'
# members_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "xh8yej3", " " )) and (((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "xo1l8bm", " " )) and contains(concat( " ", @class, " " ), concat( " ", "xzsf02u", " " ))]'
members_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "x14l7nz5", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "x1xmf6yo", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "xh8yej3", " " )) and (((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "xzsf02u", " " ))]'
las_week_members_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "x14l7nz5", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "x1xmf6yo", " " ))]//*+[contains(concat( " ", @class, " " ), concat( " ", "xh8yej3", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "xh8yej3", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "xi81zsa", " " ))]'
today_post_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "x16tdsg8", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "xo1l8bm", " " )) and contains(concat( " ", @class, " " ), concat( " ", "xzsf02u", " " ))]'
last_month_post_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "x16tdsg8", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "xi81zsa", " " )) and contains(concat( " ", @class, " " ), concat( " ", "x1yc453h", " " ))]'
# created_at_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "x14l7nz5", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "x1xmf6yo", " " ))]//*~[contains(concat( " ", @class, " " ), concat( " ", "xh8yej3", " " ))]//*+[contains(concat( " ", @class, " " ), concat( " ", "xh8yej3", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "xh8yej3", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "x1yc453h", " " ))]'
########################################


# GET THE EXACT DATE OF GROUP CREATED
def extract_creation_date(description):
    current_date = datetime.now()
    
    if 'years' in description:
        years = int(description.split()[1])
        creation_date = current_date - timedelta(days=365 * years)
    elif 'weeks' in description:
        weeks = int(description.split()[1])
        creation_date = current_date - timedelta(weeks=weeks)
    elif 'days' in description:
        days = int(description.split()[1])
        creation_date = current_date - timedelta(days=days)
    else:
        # Handle unrecognized format
        creation_date = None
    
    return creation_date

# Function to check if the Excel file exists
def excel_file_exists(file_path):
    return os.path.exists(file_path)

# Function to write data to Excel
def write_to_excel(data, file_path):
    # If file exists, load the existing data and append new data
    if excel_file_exists(file_path):
        existing_data = pd.read_excel(file_path)
        updated_data = pd.concat([existing_data, data], ignore_index=True)
        updated_data.to_excel(file_path, index=False)
    else:
        # If file does not exist, write new data to Excel
        data.to_excel(file_path, index=False)

# Load existing URLs from Excel
def load_existing_urls_from_excel(excel_file):
    df = pd.read_excel(excel_file)
    print('---->>> checking excel file already had the group url or not ...')
    print(df)
    print('---->>> -------------------------------------.....')
    return df['Group URL'].tolist()

# Function to extract clean group links from anchor tags
def extract_clean_group_links(anchors, existing_urls):
    clean_group_links = []
    for a in anchors:
        if a.startswith("https://www.facebook.com/groups"):
            parsed_url = urlparse(a)
            clean_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
            
            if clean_url == 'https://www.facebook.com/groups/':
                continue

            if clean_url not in existing_urls:
                clean_group_links.append(clean_url)

            clean_group_links.append(clean_url)
    # Remove duplicate links
    clean_group_links = list(set(clean_group_links))
    return clean_group_links

# Function to get group details
def get_group_details(driver, group_details_xpath):
    group_details_elements = driver.find_elements(By.XPATH, group_details_xpath)
    group_details = {}
    for element in group_details_elements:
        get_group_name = driver.find_element(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "xt0b8zv", " " )) and contains(concat( " ", @class, " " ), concat( " ", "x1xlr1w8", " " ))]')
        group_details["Group Name"] = get_group_name.text.strip()
        text = element.text.strip()
        if text:
            if "Public" in text or "Private" in text:
                group_details["Group Status"] = text
            elif "Visible" in text or "Hidden" in text:
                group_details["Visible Status"] = text
            elif "History" in text or "Tags" in text:
                pass
            else:
                group_details["Location"] = text
    return group_details

# Function to scroll and get groups
def scroll_to_get_group(driver, group_details_xpath, members_xpath, search_keyword, excel_file):
    anchors = driver.find_elements(By.TAG_NAME, 'a')
    anchors = [a.get_attribute('href') for a in anchors]

    # extract the excel url 
    existing_urls = load_existing_urls_from_excel(excel_file)
    clean_group_links = extract_clean_group_links(anchors, existing_urls)
    group_data = []
    for group_url in clean_group_links:
        print('--->>> gropu url -> ', group_url)

        # Checking if the URL contains "/posts/", if so, skip processing
        if "/posts/" in group_url:
            print('Skipping URL containing "/posts/":', group_url)
            continue

        if "/create/" in group_url:
            print('Skipping URL containing "/posts/":', group_url)
            continue

        # checking if our group link already exist in excel file
        if group_url in existing_urls:
            print('Group already in excel file. Skipping..')
            continue

        # if group url not exist in excel file then continue further process
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(group_url + 'about/')

        ########################################
        # START - EXTRACTING DATA FROM WEBPAGE
        ########################################
        group_details_about = get_group_details(driver, group_details_xpath)
        group_members = driver.find_element(By.XPATH, members_xpath).text.strip()
        # las_week_members = driver.find_element(By.XPATH, las_week_members_xpath)
        today_post = driver.find_element(By.XPATH, today_post_xpath).text.strip()
        # last_month_post = driver.find_element(By.XPATH, last_month_post_xpath).text.strip()
        # created_at = driver.find_element(By.XPATH, created_at_xpath).text.strip()
        group_data.append({
            "Keyword": search_keyword,
            "Group Name": group_details_about.get("Group Name", "Not available"),
            "Group URL": group_url,
            "Group Status": group_details_about.get("Group Status", "Not available"),
            "Visible Status": group_details_about.get("Visible Status", "Not available"),
            "Location": group_details_about.get("Location", "Not available"),
            "Members": group_members,
            # "Last Week Joined Members": las_week_members,
            "Today\'s Post": today_post if today_post else 0,
            # "Last Month Joined People": last_month_post,
            # "Group Created At": extract_creation_date(created_at),
        })
        ########################################
        # END - EXTRACTING DATA FROM WEBPAGE
        ########################################

        df = pd.DataFrame([group_data[-1]])
        write_to_excel(df, excel_file_name)
        print("Group Name:", group_data[-1].get("Group Name", "Not available"))
        print("Group URL:", group_url)
        print("Group Status:", group_data[-1].get("Group Status", "Not available"))
        print("-" * 20)

        time.sleep(2)
        driver.close()
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[0])

# Main function
def main():
    # Configure driver
    service = Service(executable_path='C:/Hossain Foysal/Software/chromedriver-win64/chromedriver.exe')
    options = webdriver.ChromeOptions()
    prefs = {
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)

    # Open the website and login
    driver.get("https://facebook.com")
    username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
    password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))
    username.clear()
    username.send_keys(os.getenv('FB_USERNAME'))
    password.clear()
    password.send_keys(os.getenv('FB_PASSWORD'))
    button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
    time.sleep(2)

    # Start searching for groups
    group_search_url = f"https://www.facebook.com/search/groups?q={search_keyword}&filters=eyJmaWx0ZXJfZ3JvdXBzX2xvY2F0aW9uOjAiOiJ7XCJuYW1lXCI6XCJmaWx0ZXJfZ3JvdXBzX2xvY2F0aW9uXCIsXCJhcmdzXCI6XCIxMDE4ODk1ODY1MTkzMDFcIn0ifQ%3D%3D"
    driver.get(group_search_url)
    time.sleep(5)

    # Create Excel file if it doesn't exist
    global excel_file_name
    excel_file_name = f"{slugify(search_keyword)}_facebook_groups_dataset.xlsx"
    if not excel_file_exists(excel_file_name):
        with pd.ExcelWriter(excel_file_name, mode='w', engine='openpyxl') as writer:
            pd.DataFrame().to_excel(writer, index=False)

    # Scroll and collect group data
    while True:
        scroll_to_get_group(driver, group_details_xpath, members_xpath, search_keyword=search_keyword, excel_file=excel_file_name)
        time.sleep(5)
        for _ in range(100):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
        if len(pd.read_excel(excel_file_name)) >= target_leads:
            break

    # Close the driver
    driver.quit()

if __name__ == "__main__":
    # Set parameters
    search_keyword = 'buy and sell'
    target_leads = 500
    main()