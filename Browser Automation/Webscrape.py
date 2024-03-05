from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import time

def init_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    
    browser = webdriver.Chrome(options=options)
    return browser


def login_to_linkedin(browser, username, password):
    try:
        browser.get("https://www.linkedin.com/login")
        time.sleep(2) 
        username_field = browser.find_element(By.ID, "username")
        password_field = browser.find_element(By.ID, "password")
        login_button = browser.find_element(By.CSS_SELECTOR, ".login__form_action_container button")

        username_field.send_keys(username)
        password_field.send_keys(password)

        login_button.click()

        time.sleep(10)  
        
        if "feed" not in browser.current_url:
            raise Exception("Failed to login. Please check your credentials.")

    except Exception as e:
        print("Error:", e)
        exit()

def search_linkedin_users(browser, search_query):
    search_box = browser.find_element(By.CSS_SELECTOR, "input.search-global-typeahead__input")
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)
    people_button = browser.find_element(By.CLASS_NAME, 'artdeco-pill--choice')
    people_button.click()
    time.sleep(2)

def extract_user_data(browser):
    time.sleep(5)
    page_source = browser.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    user_data_list = []

    search_results = soup.find_all("li", class_="reusable-search__result-container")

    for result in search_results[:10]: 
        name_element = result.find('span', {'aria-hidden': 'true'})
        name = name_element.get_text(strip=True) if name_element else "N/A"

        primary_title_element = result.find("div", class_="entity-result__primary-subtitle t-14 t-black t-normal")
        primary_title = primary_title_element.get_text(strip=True) if primary_title_element else "N/A"

        secondary_title_element = result.find("div", class_="entity-result__secondary-subtitle t-14 t-normal")
        secondary_title = secondary_title_element.get_text(strip=True) if secondary_title_element else "N/A"

        user_data = {
            "Name": name,
            "Title": primary_title,
            "Location": secondary_title
            \
        }
        user_data_list.append(user_data)
       
        print("Extracted user data:", user_data)

    return user_data_list

def save_to_csv(user_data_list, csv_filename):
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ["Name", "Title", "Location"]  
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for user_data in user_data_list:
            writer.writerow(user_data)
            print("User data saved to CSV:", user_data)


if __name__ == "__main__":
    linkedin_username = input("Enter Email: ")
    linkedin_password = "your password here"  

    search_query = input("Enter Name to search: ")
    csv_filename = "linkedin_data.csv"

    browser = init_browser()
    login_to_linkedin(browser, linkedin_username, linkedin_password)
    search_linkedin_users(browser, search_query)
    user_data_list = extract_user_data(browser)
    save_to_csv(user_data_list, csv_filename)

    browser.quit()
