import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import chromedriver_autoinstaller

# Set Instagram credentials
username = os.environ.get('INSTAGRAM_USERNAME', 'Your Instagram username')
password = os.environ.get('INSTAGRAM_PASSWORD', 'Your Instagram password')

# Configure ChromeDriver
chromedriver_autoinstaller.install()  # Automatically install the correct chromedriver
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-notifications')
options.add_argument('--disable-popup-blocking')
options.add_argument('--disable-infobars')
options.add_argument('--start-maximized')  # Maximize the window

# Function to log in to Instagram via Selenium
def login_to_instagram(driver, username, password):
    print("Navigating to Instagram login page...")
    driver.get('https://www.instagram.com/accounts/login/')
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    except TimeoutException as e:
        print(f"Error during login: TimeoutException {e}")
        return False
    except Exception as e:
        print(f"Error during login: {e}")
        return False
    time.sleep(5)

    # Verify if the login was successful
    try:
        driver.find_element(By.XPATH, "//div[text()='The username you entered doesn't belong to an account. Please check your username and try again.']")
        print("Error: Invalid username")
        return False
    except:
        pass

    try:
        driver.find_element(By.XPATH, "//div[text()='Sorry, your password was incorrect. Please double-check your password.']")
        print("Error: Invalid password")
        return False
    except:
        pass

    print("Login successful!")
    return True

# Function to navigate to an Instagram profile
def go_to_profile(driver, username):
    print(f"Navigating to {username}'s profile...")
    driver.get(f'https://www.instagram.com/{username}/')

# Function to click on followers
def click_on_followers(driver):
    print("Clicking on followers...")
    try:
        followers_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "follower"))
        )
        followers_link.click()
    except TimeoutException as e:
        print(f"Error clicking on followers: TimeoutException {e}")
    except Exception as e:
        print(f"Error clicking on followers: {e}")

# Function to scroll to load all followers
def scroll_to_load_followers(driver):
    print("Scrolling to load all followers...")
    try:
        fBody = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='isgrP']"))
        )
        scroll = 0
        while scroll < 5:  # Increase this value to scroll longer
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', fBody)
            time.sleep(2)
            scroll += 1
    except TimeoutException as e:
        print(f"Error scrolling through followers: TimeoutException {e}")
    except Exception as e:
        print(f"Error scrolling through followers: {e}")

# Function to extract followers' links
def extract_followers_links(driver):
    print("Extracting followers' links...")
    try:
        followers_elems = driver.find_elements(By.XPATH, "//a[@class='FPmhX notranslate _0imsa ']")
        followers = [elem.get_attribute('href') for elem in followers_elems]
        return followers
    except Exception as e:
        print(f"Error extracting followers' links: {e}")
        return []

# Function to identify spammers
def identify_spammers(driver, followers):
    print("Identifying spammers...")
    spammers = []
    for follower in followers:
        try:
            driver.get(follower)
            time.sleep(10)

            is_private = False
            try:
                is_private = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h2[text()='This Account is Private']"))
                )
            except TimeoutException:
                pass
            if is_private:
                continue

            # Check if the username appears to be a spammer
            follower_username = follower.split("/")[-2]
            if "bot" in follower_username.lower() or "spam" in follower_username.lower():
                spammers.append(follower_username)
                continue  # Skip detailed analysis for this follower

            # Perform detailed profile analysis to identify spammers
            biography_elem = driver.find_element(By.XPATH, "//div[@class='-vDIg']//span")
            biography = biography_elem.text if biography_elem else ""
            if not biography:
                continue

            try:
                followers_count = int(driver.find_element(By.XPATH, "//a[contains(@href,'/followers')]/span").text.replace(',', ''))
                following_count = int(driver.find_element(By.XPATH, "//a[contains(@href,'/following')]/span").text.replace(',', ''))
            except Exception:
                followers_count, following_count = 0, 0

            if followers_count < 100 or following_count > 1000:
                spammers.append(follower_username)

            try:
                story_count = int(driver.find_element(By.XPATH, "//div[@class='ySN3v']//div[contains(@class,'eLAPa')]").text)
                if story_count == 0 or story_count > 100:
                    spammers.append(follower_username)
            except Exception:
                pass

        except Exception as e:
            print(f"Error analyzing profile {follower}: {str(e)}")
            continue

    return spammers

# Log in to Instagram via Selenium
driver = webdriver.Chrome(options=options)

try:
    if login_to_instagram(driver, username, password):
        # Navigate to profile and click on followers
        go_to_profile(driver, username)
        click_on_followers(driver)

        # Scroll to load all followers and extract their links
        scroll_to_load_followers(driver)
        followers = extract_followers_links(driver)

        # Identify spammers
        spammers = identify_spammers(driver, followers)

        # Print the list of identified bot spammers
        print("Identified bot spammers:")
        if spammers:
            for spammer in spammers:
                print(spammer)
        else:
            print("No bot spammers identified.")

finally:
    # Close the Selenium driver at the end of the execution
    driver.quit()
