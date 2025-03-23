import os
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import chromedriver_autoinstaller

# Configurazione logging
logging.basicConfig(filename='bot_detector.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Credenziali (migliorare con vault se necessario)
username = os.getenv('INSTAGRAM_USERNAME') or input("Inserisci username Instagram: ")
password = os.getenv('INSTAGRAM_PASSWORD') or input("Inserisci password Instagram: ")

# Configurazione Chrome con User-Agent casuale
def setup_driver(proxy=None):
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(f'--user-agent={random.choice(USER_AGENTS)}')
    
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    
    return webdriver.Chrome(options=options)

# User-Agents casuali per evitare il rilevamento
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    # Aggiungi altri User-Agent validi
]

def login_to_instagram(driver):
    try:
        driver.get('https://www.instagram.com/accounts/login/')
        
        # Inserimento credenziali
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        
        # Gestione 2FA manuale
        if "two_factor" in driver.current_url:
            input("Completa il 2FA sul browser, poi premi Invio qui.")
        
        # Verifica login avvenuto
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/accounts/logout/')]"))
        )
        logging.info("Login riuscito")
        return True

    except Exception as e:
        logging.error(f"Errore durante il login: {str(e)}")
        return False

def scroll_followers_list(driver):
    """Scorri la lista dei follower dinamicamente"""
    try:
        dialog = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
        )
        
        last_height = 0
        retry_count = 0
        
        while retry_count < 3:
            # Scorri fino in fondo
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', dialog)
            time.sleep(random.uniform(1.5, 2.5))
            
            # Verifica se ci sono nuovi elementi
            new_height = driver.execute_script("return arguments[0].scrollHeight", dialog)
            
            if new_height == last_height:
                retry_count += 1
            else:
                retry_count = 0
                
            last_height = new_height
            
        logging.info("Lista follower caricata completamente")
    except Exception as e:
        logging.warning(f"Errore durante lo scrolling: {str(e)}")

def analyze_profile(driver, profile_url):
    """Analisi avanzata del profilo"""
    try:
        driver.get(profile_url)
        time.sleep(random.uniform(2, 4))
        
        # Controllo account privato
        if check_private_account(driver):
            return None
            
        # Raccolta dati
        username = profile_url.split("/")[-2]
        bio = get_bio(driver)
        followers, following, posts = get_counts(driver)
        
        # Euristiche avanzate
        if (posts == 0 or 
            following > 5 * followers or 
            "buy" in bio.lower() or
            "spam" in username.lower() or
            "bot" in username.lower()):
            return username
            
        return None
    except Exception as e:
        logging.error(f"Errore analizzando {profile_url}: {str(e)}")
        return None

def check_private_account(driver):
    try:
        driver.find_element(By.XPATH, "//h2[contains(text(), 'Account privato')]")
        return True
    except NoSuchElementException:
        return False

def get_bio(driver):
    try:
        return driver.find_element(By.XPATH, "//div[@class='-vDIg']//span").text
    except:
        return ""

def get_counts(driver):
    try:
        posts = int(driver.find_element(By.XPATH, "//span[contains(@class, 'g47SY')][1]").text.replace(',', ''))
        followers = int(driver.find_element(By.XPATH, "//a[contains(@href, '/followers')]/span").text.replace(',', ''))
        following = int(driver.find_element(By.XPATH, "//a[contains(@href, '/following')]/span").text.replace(',', ''))
        return followers, following, posts
    except:
        return 0, 0, 0

# MAIN
if __name__ == "__main__":
    driver = setup_driver(proxy=os.getenv('PROXY'))  # Opzionale: aggiungi proxy
    try:
        if not login_to_instagram(driver):
            raise Exception("Login fallito")
            
        # Apri lista follower (modifica con il tuo username)
        driver.get(f"https://www.instagram.com/{username}/followers/")
        scroll_followers_list(driver)
        
        # Estrai tutti i profili
        followers = [elem.get_attribute('href') for elem in 
                    driver.find_elements(By.XPATH, "//a[@class='FPmhX notranslate _0imsa ']")]
        
        # Analizza ogni profilo
        spammers = []
        for i, follower in enumerate(followers):
            if i % 10 == 0:  # Limita le richieste per evitare blocchi
                time.sleep(random.uniform(60, 120))
                
            spammer = analyze_profile(driver, follower)
            if spammer:
                spammers.append(spammer)
                logging.warning(f"Bot rilevato: {spammer}")
        
        print(f"Bot rilevati ({len(spammers)}):")
        print("\n".join(spammers))
                
    except Exception as e:
        logging.critical(f"Errore critico: {str(e)}")
    finally:
        driver.quit()
