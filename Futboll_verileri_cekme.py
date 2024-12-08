import pandas as pd
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
import re
import traceback
import random
import logging
from warnings import filterwarnings
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
filterwarnings('ignore')

# DataFrame için sütun isimleri
keys = [
    'Country',
    'Lig',
    'home_team',
    'away_team',
    'home_score',
    'away_score',
    'season_year',
    'Date_day',
    'Date_hour',
    'first_half',
    'second_half',
    
    'home_team_goals_current_time',
    'home_team_goals_current_score',
    'home_team_goals',
    'home_team_goals_assist',
    
    'away_team_goals_current_time',
    'away_team_goals_current_score',
    'away_team_goals',
    'away_team_goals_assist',

    'home_team_yellow_card_current_time',
    'home_team_yellow_card',
    'home_team_yellow_card_why',

    'away_team_yellow_card_current_time',
    'away_team_yellow_card',
    'away_team_yellow_card_why',

    'home_team_red_card_current_time',
    'home_team_red_card',
    'home_team_red_card_why',
    
    'away_team_red_card_current_time',
    'away_team_red_card',
    'away_team_red_card_why',
    
    'home_team_substitutions_current_time',
    'home_team_substitutions',
    'home_team_substitutions_with',
    'home_team_substitution_why',
    
    'away_team_substitutions_current_time',
    'away_team_substitutions',
    'away_team_substitutions_with',
    'away_team_substitution_why',
    
    'expected_goals_xg_home' ,
    'expected_goals_xg_host' ,
    
    'Ball_Possession_Home' ,
    'Ball_Possession_Host' ,
    
    'Goal_Attempts_Home' ,
    'Goal_Attempts_Host' ,
    
    'Shots_on_Goal_Home' ,
    'Shots_on_Goal_Host' ,
    
    'Shots_off_Goal_Home' ,
    'Shots_off_Goal_Host' ,
    
    'Blocked_Shots_Home' ,
    'Blocked_Shots_Host' ,
    
    'Free_Kicks_Home' ,
    'Free_Kicks_Host' ,
    
    'Corner_Kicks_Home' ,
    'Corner_Kicks_Host' ,
    
    'Offsides_Home' ,
    'Offsides_Host' ,
    
    'Throw_ins_Home' ,
    'Throw_ins_Host' ,
    
    'Goalkeeper_Saves_Home' ,
    'Goalkeeper_Saves_Host' ,
    
    'Fouls_Home' ,
    'Fouls_Host' ,
    
    'Red_Cards_Home' ,
    'Red_Cards_Host' ,
    
    'Yellow_Cards_Home' ,
    'Yellow_Cards_Host' ,
    
    'Total_Passes_Home' ,
    'Total_Passes_Host' ,
    
    'Completed_Passes_Home' ,
    'Completed_Passes_Host' ,
    
    'Tackles_Home' ,
    'Tackles_Host' ,
    
    'Crosses_Completed_Home' ,
    'Crosses_Completed_Host' ,
    
    'Interceptions_Home' ,
    'Interceptions_Host',
    
    'Attacks_Home',
    'Attacks_Host',
    
    'Dangerous_Attacks_Home' ,
    'Dangerous_Attacks_Host',
    
    'Distance_Covered_(km)_Home',
    'Distance_Covered_(km)_Host',
    
    'Clearances_Completed_Home',
    'Clearances_Completed_Host',
    
    'Pass_Success_per_Home',
    'Pass_Success_per_Host',
    
    'referee',
    'venue',
    'capacity',
    'attendance',
    
]

# Global DataFrame
df = pd.DataFrame(columns=keys)


def wait_for_element(driver, by, value, timeout=10, condition="presence"):
    """
    Wait for an element with better error handling and retries
    """
    try:
        if condition == "presence":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        elif condition == "clickable":
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        elif condition == "visible":
            element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
        return element
    except StaleElementReferenceException:
        time.sleep(1)
        return wait_for_element(driver, by, value, timeout, condition)
    except TimeoutException:
        return None

def format_league_for_url(league_name):
    # Lig adlarını URL formatına çevir
    league_mapping = {
        "Super Lig": "super-lig",
        "1. Lig": "1-lig",
        "Premier League": "premier-league",
        "LaLiga": "laliga",
        "Bundesliga": "bundesliga",
        "Serie A": "serie-a",
        "Ligue 1": "ligue-1"
    }
    return league_mapping.get(league_name, league_name.lower().replace(' ', '-'))

def get_league_url(league):
    return format_league_for_url(league)

def initialize_driver():
    try:
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-features=NetworkService')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # User agent ekleme
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Performance ayarları
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-notifications')
        
        # Page load strategy
        caps = DesiredCapabilities.CHROME
        caps['pageLoadStrategy'] = 'eager'  # DOM hazır olduğunda devam et
        
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options, desired_capabilities=caps)
        
        # Timeouts
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        # JavaScript beklemelerini ayarla
        driver.execute_script("""
            window.addEventListener('load', function() {
                window.isPageLoaded = true;
            });
            
            // Network isteklerini izle
            let openRequests = 0;
            let originalOpen = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function() {
                openRequests++;
                this.addEventListener('loadend', function() {
                    openRequests--;
                });
                originalOpen.apply(this, arguments);
            };
            
            // Network isteklerinin tamamlanmasını bekle
            window.waitForRequests = function() {
                return new Promise((resolve) => {
                    if (openRequests === 0) {
                        resolve();
                    } else {
                        let interval = setInterval(() => {
                            if (openRequests === 0) {
                                clearInterval(interval);
                                resolve();
                            }
                        }, 100);
                    }
                });
            };
        """)
        
        return driver
    except Exception as e:
        logger.error(f"Error initializing driver: {str(e)}")
        raise

def wait_for_page_load(driver, timeout=30):
    try:
        # DOM yüklenmesini bekle
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # JavaScript yüklenmesini bekle
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return typeof window.isPageLoaded !== 'undefined'")
        )
        
        # Network isteklerinin tamamlanmasını bekle
        driver.execute_script("return window.waitForRequests()")
        
        # Görünür elementlerin yüklenmesini bekle
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Kısa bir bekleme ekle
        time.sleep(2)
        
    except Exception as e:
        logger.warning(f"Page load wait warning: {str(e)}")

def scrap(country_link_name, leagues, years):
    global df
    logger.info(f"\nStarting scraping for:")
    logger.info(f"Country: {country_link_name}")
    logger.info(f"Leagues: {leagues}")
    logger.info(f"Years: {years}")
    
    try:
        for league in leagues:
            lig_url = get_league_url(league)
            
            # URL oluştur
            url = "https://www.flashscore.com/football/" + country_link_name +"/" + lig_url +"/"
            logger.info(f"\nScraping URL: {url}")
            
            path = "/Users/muhammedaydin/Desktop/driverchrome/chromedriver"
            service = Service(path)
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-notifications")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            try:
                driver.get(url)
                
                # Sayfa yüklenmesini bekle
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(3)
                
                # Handle cookie consent with multiple attempts
                try:
                    cookie_selectors = [
                        (By.ID, "onetrust-accept-btn-handler"),
                        (By.ID, "onetrust-reject-all-handler"),
                        (By.CLASS_NAME, "fc-button-label")
                    ]
                    
                    for selector in cookie_selectors:
                        try:
                            cookie_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable(selector)
                            )
                            safe_click(driver, cookie_button)
                            logger.info("Found and clicked cookie button")
                            time.sleep(2)
                            break
                        except:
                            continue
                except:
                    logger.warning("No cookie button found or already accepted")
                
                for year in years:
                    logger.info(f"\nScraping league: {league}, year: {year}")
                    
                    try:
                        # Try multiple selectors for archive button
                        archive_selectors = [
                            (By.CLASS_NAME, "archive__button"),
                            (By.CLASS_NAME, "archive"),
                            (By.XPATH, "//button[contains(@class, 'archive')]"),
                            (By.XPATH, "//div[contains(@class, 'archive')]")
                        ]
                        
                        archive_button = None
                        for selector in archive_selectors:
                            try:
                                archive_button = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable(selector)
                                )
                                if archive_button:
                                    break
                            except:
                                continue
                        
                        if archive_button:
                            # Scroll to archive button
                            driver.execute_script("arguments[0].scrollIntoView(true);", archive_button)
                            time.sleep(1)
                            
                            # Try to click with both Selenium and JavaScript
                            try:
                                # First try JavaScript click
                                driver.execute_script("arguments[0].click();", archive_button)
                            except:
                                try:
                                    # Then try regular click
                                    archive_button.click()
                                except:
                                    continue
                        
                            logger.info("Found and clicked archive button")
                            time.sleep(2)
                        else:
                            logger.error("Could not find archive button with any selector")
                            continue
                        
                        # Process the year selection
                        if not select_year(driver, year):
                            logger.warning(f"Year {year} not found, skipping...")
                            continue
                        
                        # Load more matches
                        more_button(driver)
                        
                        # Remove ads for better scraping
                        remove_ads(driver)
                        
                        # Scrape match data
                        matches_found = scrape_everything(driver, country_link_name, league, year)
                        
                        # Save to CSV periodically
                        df.to_csv(f"football_data_{country_link_name}_{league.lower().replace(' ', '_').replace('.','')}.csv", index=False)
                        logger.info(f"Data saved to football_data_{country_link_name}_{league.lower().replace(' ', '_').replace('.','')}.csv")
                        
                    except Exception as e:
                        logger.error(f"Error processing year {year}: {str(e)}")
                        traceback.print_exc()
                        continue
                    
            except Exception as e:
                logger.error(f"Error processing league {league}: {str(e)}")
                traceback.print_exc()
            finally:
                driver.quit()
                
    except Exception as e:
        logger.error(f"Fatal error in scraping: {str(e)}")
        traceback.print_exc()
    
    return df

def select_year(driver, year):
    try:
        # Archive butonunu bul ve tıkla
        archive_selectors = [
            (By.CSS_SELECTOR, '[class*="archive"]'),
            (By.CSS_SELECTOR, '[class*="archive__button"]'),
            (By.XPATH, "//div[contains(@class, 'archive')]"),
            (By.XPATH, "//button[contains(@class, 'archive')]")
        ]
        
        archive_clicked = False
        for selector in archive_selectors:
            try:
                archive_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(selector)
                )
                if archive_button and archive_button.is_displayed():
                    # Scroll into view and click
                    driver.execute_script("arguments[0].scrollIntoView(true);", archive_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", archive_button)
                    archive_clicked = True
                    logger.info("Found and clicked archive button")
                    time.sleep(3)
                    break
            except Exception as e:
                logger.error(f"Error clicking archive button with selector {selector}: {str(e)}")
                continue
        
        if not archive_clicked:
            logger.error("Could not click any archive button")
            return False
        
        # Wait for season menu to load
        time.sleep(3)
        
        # Find season elements using JavaScript
        season_elements = driver.execute_script("""
            function findSeasonElements() {
                // Define selectors for season elements
                const selectors = [
                    '.archive__season',
                    '[class*="archive"] [class*="season"]',
                    '[class*="league"] [class*="season"]',
                    '[class*="tournament"] [class*="season"]',
                    '[class*="archive__"] a',  // Archive links
                    '[class*="season__"] a'    // Season links
                ];
                
                let seasonElements = [];
                
                // Try each selector
                for (let selector of selectors) {
                    let elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        seasonElements = [...seasonElements, ...Array.from(elements)];
                    }
                }
                
                // If no elements found with class selectors, try finding by text content
                if (seasonElements.length === 0) {
                    document.querySelectorAll('a, div, span').forEach(el => {
                        let text = el.textContent.trim();
                        if (text && (
                            text.includes('20') ||        // Year format: 2023
                            text.includes('/') ||         // Year format: 2023/24
                            text.includes('-') ||         // Year format: 2023-24
                            /\d{2}\/\d{2}/.test(text) || // Year format: 23/24
                            /\d{4}/.test(text)           // Any 4-digit number
                        )) {
                            seasonElements.push(el);
                        }
                    });
                }
                
                // Filter out any hidden or non-interactive elements
                return seasonElements.filter(el => {
                    let style = window.getComputedStyle(el);
                    return el.offsetParent !== null &&  // Element is visible
                           style.display !== 'none' &&
                           style.visibility !== 'hidden' &&
                           el.getBoundingClientRect().height > 0;
                });
            }
            return findSeasonElements();
        """)
        
        if not season_elements:
            logger.error("Could not find season elements with JavaScript")
            # Try XPath as a fallback
            try:
                season_elements = driver.find_elements(By.XPATH, 
                    "//*[contains(@class, 'season') or contains(text(), '2023') or contains(text(), '/')]")
            except:
                pass
        
        if not season_elements:
            logger.error("Could not find any season elements")
            return False
        
        logger.info(f"Found {len(season_elements)} season elements")
        
        # Check seasons
        year_patterns = [
            str(year),                          # 2023
            f"{year}/{int(year)+1}",           # 2023/2024
            f"{year}-{int(year)+1}",           # 2023-2024
            f"{str(year)[-2:]}/{int(str(year)[-2:])+1}"  # 23/24
        ]
        
        for element in season_elements:
            try:
                # Get element text safely
                season_text = driver.execute_script("""
                    function getElementText(el) {
                        if (!el) return '';
                        return el.textContent || el.innerText || '';
                    }
                    return getElementText(arguments[0]);
                """, element)
                
                if not season_text:
                    continue
                    
                season_text = season_text.strip()
                logger.info(f"Checking season element: {season_text}")
                
                # Check year pattern match
                for pattern in year_patterns:
                    if pattern.lower() in season_text.lower():
                        logger.info(f"Found matching year pattern {pattern} in {season_text}")
                        
                        # Make sure element is visible
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                        time.sleep(1)
                        
                        # Try clicking with retry
                        try:
                            # First try JavaScript click
                            driver.execute_script("arguments[0].click();", element)
                        except:
                            try:
                                # Then try regular click
                                element.click()
                            except:
                                continue
                        
                        time.sleep(2)
                        return True
                        
            except Exception as e:
                logger.error(f"Error processing season element: {str(e)}")
                continue
        
        logger.warning(f"Year {year} not found, skipping...")
        return False
        
    except Exception as e:
        logger.error(f"Error in select_year: {str(e)}")
        return False

def select_country_league(driver, country, league):
    try:
        # Ülke seçimi için bekle ve tıkla
        country_xpath = f"//div[contains(@class, 'lmenu__title') and contains(text(), '{country}')]"
        country_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, country_xpath))
        )
        
        # Ülke elementini görünür yap ve tıkla
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", country_element)
        time.sleep(1)
        
        # JavaScript ile tıkla
        driver.execute_script("arguments[0].click();", country_element)
        logger.info(f"Clicked country: {country}")
        time.sleep(2)
        
        # Lig seçimi için bekle
        league_selectors = [
            f"//div[contains(@class, 'lmenu__text') and contains(text(), '{league}')]",
            f"//div[contains(@class, 'lmenu__item') and contains(., '{league}')]",
            f"//a[contains(@class, 'lmenu__item') and contains(., '{league}')]"
        ]
        
        league_found = False
        for selector in league_selectors:
            try:
                league_element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                
                # Lig elementini görünür yap
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", league_element)
                time.sleep(1)
                
                # JavaScript ile tıkla
                driver.execute_script("arguments[0].click();", league_element)
                logger.info(f"Clicked league: {league}")
                league_found = True
                break
            except:
                continue
        
        if not league_found:
            # Alternatif yöntem: JavaScript ile bul ve tıkla
            league_found = driver.execute_script("""
                function findAndClickLeague(leagueName) {
                    // Tüm menü öğelerini kontrol et
                    let elements = document.querySelectorAll('[class*="lmenu__"], [class*="menuMinority__"]');
                    for (let el of elements) {
                        if (el.textContent.includes(leagueName)) {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                }
                return findAndClickLeague(arguments[0]);
            """, league)
        
        if not league_found:
            logger.error(f"Could not find league: {league}")
            return False
        
        # Sayfanın yüklenmesi için bekle
        time.sleep(3)
        
        # Sayfa yüklenme kontrolü
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error in select_country_league: {str(e)}")
        return False

def more_button(driver):
    try:
        # Daha fazla maç butonunu bul ve tıkla
        while True:
            try:
                more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[@class="event__more event__more--static"]'))
                )
                print("Found more button, clicking...")
                more_button.click()
                time.sleep(1)  # Her tıklamadan sonra bekle
            except:
                print("No more matches to load")
                break
    except Exception as e:
        print(f"Error in more_button: {e}")
        pass

def remove_ads(driver):
    try:
        # Reklamları kaldır
        driver.execute_script("""
            var elements = document.querySelectorAll('iframe, [id*="advertisement"], [class*="advertisement"], [id*="banner"], [class*="banner"]');
            for(var i=0; i<elements.length; i++){
                elements[i].style.display = 'none';
            }
        """)
        print("Advertisements removed")
    except Exception as e:
        print(f"Error removing ads: {e}")

def safe_click(driver, element, max_retries=3):
    """
    Improved safe click function with better stale element handling
    """
    for attempt in range(max_retries):
        try:
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(1)
            
            # Try direct click first
            try:
                element.click()
                return True
            except:
                # If direct click fails, try JavaScript click
                driver.execute_script("arguments[0].click();", element)
                return True
                
        except StaleElementReferenceException:
            if attempt == max_retries - 1:
                logger.error("Element became stale and all retry attempts failed")
                return False
                
            # Try to re-find the element using its properties
            try:
                # Get element properties before it becomes stale
                element_tag = driver.execute_script("return arguments[0].tagName;", element).lower()
                element_class = driver.execute_script("return arguments[0].className;", element)
                element_id = driver.execute_script("return arguments[0].id;", element)
                
                # Wait for page to stabilize
                time.sleep(2)
                
                # Try to re-find element
                if element_id:
                    element = wait_for_element(driver, By.ID, element_id, condition="clickable")
                elif element_class:
                    element = wait_for_element(driver, By.CLASS_NAME, element_class, condition="clickable")
                else:
                    element = wait_for_element(driver, By.TAG_NAME, element_tag, condition="clickable")
                    
                if not element:
                    continue
                    
            except Exception as e:
                logger.error(f"Error re-finding element: {str(e)}")
                continue
                
        except Exception as e:
            logger.error(f"Error clicking element: {str(e)}")
            if attempt == max_retries - 1:
                return False
            time.sleep(2)
            
    return False

def scrape_everything(driver, county, lig, year):
    global df
    matches_found = 0
    retry_count = 0
    max_retries = 3
    
    def refresh_page_state():
        driver.execute_script("""
            window.scrollTo(0, 0);
            document.body.style.zoom = '100%';
            document.body.style.transform = 'scale(1)';
        """)
        time.sleep(2)
    
    try:
        # Remove ads and wait for page load
        remove_ads(driver)
        wait_for_page_load(driver)
        
        # Initial page setup
        logger.info("Setting up page for scraping...")
        
        # Wait for dynamic content and scroll
        time.sleep(5)
        
        # Scroll through the page to load all content
        total_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(0, total_height, 500):
            driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(0.5)
        
        # Scroll back to top and refresh page state
        refresh_page_state()
        
        # Click "More matches" button if it exists
        more_button(driver)
        time.sleep(5)
        
        # Process matches
        page = 1
        while True:
            logger.info(f"\nProcessing page {page}")
            
            # Wait for page load after navigation
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("""
                        return document.readyState === 'complete' && 
                               !document.querySelector('.loading') &&
                               !document.querySelector('[class*="loader"]')
                    """)
                )
            except TimeoutException:
                logger.warning("Timeout waiting for page load")
            
            # Find matches with retry mechanism
            matches = None
            for attempt in range(max_retries):
                try:
                    matches = find_match_elements(driver)
                    if matches:
                        break
                    else:
                        logger.warning(f"No matches found on attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            driver.refresh()
                            time.sleep(5)
                except Exception as e:
                    logger.error(f"Error finding matches on attempt {attempt + 1}: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
            
            if not matches:
                logger.error("Failed to find any matches after all retries")
                break
            
            # Process each match
            for match in matches:
                try:
                    # Verify element is still valid before processing
                    if not driver.execute_script("return arguments[0].isConnected", match):
                        continue
                    
                    # Get match info with retry mechanism
                    match_info = None
                    for attempt in range(3):
                        try:
                            match_info = driver.execute_script("""
                                function getMatchInfo(element) {
                                    if (!element || !element.isConnected) return null;
                                    
                                    function findTeamNames(el) {
                                        const selectors = [
                                            '.event__participant', '.participant__participantName',
                                            '.event__team', '.teamName', '[class*="team"]'
                                        ];
                                        
                                        for (let selector of selectors) {
                                            let teams = el.querySelectorAll(selector);
                                            if (teams.length >= 2) {
                                                return {
                                                    home: teams[0].textContent.trim(),
                                                    away: teams[1].textContent.trim()
                                                };
                                            }
                                        }
                                        
                                        let parent = el.closest('[class*="event__match"]') || el.closest('[class*="gameRow"]');
                                        if (parent) {
                                            for (let selector of selectors) {
                                                let teams = parent.querySelectorAll(selector);
                                                if (teams.length >= 2) {
                                                    return {
                                                        home: teams[0].textContent.trim(),
                                                        away: teams[1].textContent.trim()
                                                    };
                                                }
                                            }
                                        }
                                        
                                        return null;
                                    }
                                    
                                    let teams = findTeamNames(element);
                                    if (!teams) return null;
                                    
                                    return {
                                        home_team: teams.home,
                                        away_team: teams.away,
                                        href: element.href || element.querySelector('a')?.href || '',
                                        visible: true
                                    };
                                }
                                return getMatchInfo(arguments[0]);
                            """, match)
                            if match_info:
                                break
                        except:
                            time.sleep(1)
                    
                    if not match_info or not match_info.get('visible'):
                        continue
                    
                    logger.info(f"\nProcessing match: {match_info['home_team']} vs {match_info['away_team']}")
                    
                    # Handle match navigation
                    try:
                        if match_info.get('href'):
                            driver.get(match_info['href'])
                        else:
                            # Scroll and click
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", match)
                            time.sleep(2)
                            
                            if not safe_click(driver, match):
                                logger.error("Failed to click match element")
                                continue
                        
                        # Wait for match details page
                        WebDriverWait(driver, 10).until(
                            lambda d: d.execute_script("""
                                return document.readyState === 'complete' && 
                                       !document.querySelector('.loading') &&
                                       !document.querySelector('[class*="loader"]')
                            """)
                        )
                        time.sleep(3)
                        
                        # Get match details
                        match_details = get_match_details(driver)
                        if match_details:
                            match_details['Country'] = county
                            match_details['League'] = lig
                            match_details['Season'] = year
                            match_details.update(match_info)
                            
                            # Add to DataFrame
                            df = pd.concat([df, pd.DataFrame([match_details])], ignore_index=True)
                            matches_found += 1
                            logger.info("Successfully added match data")
                        
                        # Navigate back
                        driver.back()
                        time.sleep(3)
                        
                    except Exception as e:
                        logger.error(f"Error processing match details: {str(e)}")
                        try:
                            driver.back()
                            time.sleep(2)
                        except:
                            pass
                        continue
                    
                except StaleElementReferenceException:
                    logger.warning("Encountered stale element, refreshing matches")
                    matches = find_match_elements(driver)
                    continue
                    
                except Exception as e:
                    logger.error(f"Error processing match: {str(e)}")
                    continue
            
            # Check for next page or more matches
            try:
                next_button = wait_for_element(driver, By.CSS_SELECTOR, '.event__more.event__more--static', timeout=5, condition="visible")
                if next_button and next_button.is_displayed():
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(3)
                    page += 1
                else:
                    break
            except:
                break
            
    except Exception as e:
        logger.error(f"Error in scrape_everything: {str(e)}")
        traceback.print_exc()
    
    logger.info(f"Successfully scraped {matches_found} matches total")
    return matches_found

def find_match_elements(driver):
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Wait for page load with improved stability check
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("""
                    return document.readyState === 'complete' && 
                           !document.querySelector('.loadingAnimation') &&
                           !document.querySelector('[class*="loader"]')
                """)
            )
            
            # Get matches using JavaScript with expanded selectors
            matches = driver.execute_script("""
                function findMatches() {
                    const selectors = [
                        // Primary selectors
                        '[id*="g_1_"]',
                        '.event__match',
                        '[class*="event__match"]',
                        '[class*="gameRow"]',
                        // Additional selectors for FlashScore
                        '.event__game',
                        '[class*="sportName soccer"]',
                        '[class*="event_"]',
                        // Specific FlashScore selectors
                        '.sportName',
                        '.event__participant',
                        // Match container selectors
                        '[id*="match-"]',
                        '[id*="game-"]',
                        // Generic match-related classes
                        '[class*="match"]',
                        '[class*="game"]',
                        '[class*="fixture"]'
                    ];
                    
                    let allMatches = new Set();
                    
                    // Try each selector
                    for (let selector of selectors) {
                        try {
                            document.querySelectorAll(selector).forEach(el => {
                                if (el && 
                                    el.isConnected && 
                                    !el.hidden &&
                                    el.offsetParent !== null) {
                                    
                                    const rect = el.getBoundingClientRect();
                                    if (rect.width > 0 && rect.height > 0) {
                                        // Additional validation for match elements
                                        const hasTeams = el.textContent.includes(' - ') || 
                                                       el.textContent.includes(' vs ') ||
                                                       el.querySelectorAll('.event__participant').length >= 2;
                                        
                                        if (hasTeams) {
                                            allMatches.add(el);
                                        }
                                    }
                                }
                            });
                        } catch (e) {
                            console.error(`Error with selector ${selector}:`, e);
                        }
                    }
                    
                    // If no matches found with primary selectors, try finding by structure
                    if (allMatches.size === 0) {
                        document.querySelectorAll('div, tr, a').forEach(el => {
                            try {
                                if (el && 
                                    el.isConnected && 
                                    !el.hidden &&
                                    el.offsetParent !== null) {
                                    
                                    const rect = el.getBoundingClientRect();
                                    if (rect.width > 0 && rect.height > 0) {
                                        const text = el.textContent || '';
                                        // Look for score patterns and team names
                                        if (text.match(/\\d+[:-]\\d+/) ||
                                            text.includes(' - ') ||
                                            text.includes(' vs ') ||
                                            (el.className && (
                                                el.className.includes('match') ||
                                                el.className.includes('game') ||
                                                el.className.includes('event')
                                            ))) {
                                            allMatches.add(el);
                                        }
                                    }
                                }
                            } catch (e) {
                                console.error('Error checking element:', e);
                            }
                        });
                    }
                    
                    return Array.from(allMatches);
                }
                return findMatches();
            """)
            
            if matches:
                logger.info(f"Found {len(matches)} matches")
                # Additional validation of found matches
                valid_matches = driver.execute_script("""
                    return arguments[0].filter(el => {
                        if (!el || !el.isConnected) return false;
                        
                        // Check if element is truly visible and interactive
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && 
                               style.visibility !== 'hidden' && 
                               style.opacity !== '0' &&
                               el.offsetParent !== null;
                    });
                """, matches)
                
                if valid_matches:
                    logger.info(f"Validated {len(valid_matches)} matches")
                    return valid_matches
                
            logger.warning(f"No matches found on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                # Enhanced scroll and refresh strategy
                driver.execute_script("""
                    const scroll = () => {
                        window.scrollTo(0, 0);
                        setTimeout(() => {
                            window.scrollTo(0, document.body.scrollHeight);
                            setTimeout(() => window.scrollTo(0, 0), 500);
                        }, 500);
                    };
                    scroll();
                    // Try to force content refresh
                    document.body.style.zoom = '0.99';
                    setTimeout(() => document.body.style.zoom = '1', 500);
                """)
                time.sleep(retry_delay)
                
                # Try clicking any "Show more" or similar buttons
                try:
                    more_buttons = driver.execute_script("""
                        return Array.from(document.querySelectorAll('button, [role="button"], a')).filter(el => {
                            const text = el.textContent.toLowerCase();
                            return text.includes('more') || 
                                   text.includes('show') || 
                                   text.includes('load') ||
                                   el.className.toLowerCase().includes('more');
                        });
                    """)
                    for button in more_buttons:
                        try:
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(1)
                        except:
                            continue
                except:
                    pass
                
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            
    return []

def analyze_page_structure(driver):
    try:
        return driver.execute_script("""
            function analyzeStructure() {
                return {
                    'eventMatches': document.querySelectorAll('div[class*="event__match"]').length,
                    'gameRows': document.querySelectorAll('div[class*="gameRow"]').length,
                    'games': document.querySelectorAll('div[class*="game"]').length,
                    'events': document.querySelectorAll('div[class*="event"]').length,
                    'matches': document.querySelectorAll('div[class*="match"]').length,
                    'soccer': document.querySelectorAll('div[class*="soccer"]').length,
                    'sport': document.querySelectorAll('div[class*="sport"]').length,
                    'teams': document.querySelectorAll('div[class*="team"]').length,
                    'participants': document.querySelectorAll('div[class*="participant"]').length
                };
            }
            return analyzeStructure();
        """)
    except Exception as e:
        logger.error(f"Error in analyze_page_structure: {str(e)}")
        return {}

def scrape_match_details(driver):

    match_info = driver.find_elements(By.CLASS_NAME, 'wcl-content_J-1BJ')

    referee = None
    venue = None
    capacity = None
    attendance = None

    full_text = " ".join([info.text.replace("\n", " ") for info in match_info])

    if "REFEREE:" in full_text:
        referee = full_text.split("REFEREE:")[1].split("VENUE:")[0].strip()
    if "VENUE:" in full_text:
        venue = full_text.split("VENUE:")[1].split("CAPACITY:")[0].strip()
    if "CAPACITY:" in full_text:
        capacity = full_text.split("CAPACITY:")[1].split("ATTENDANCE:")[0].strip()
    if "ATTENDANCE:" in full_text:
        attendance = full_text.split("ATTENDANCE:")[1].strip()

    return {
        'referee': referee,
        'venue': venue,
        'capacity': capacity,
        'attendance': attendance
    }


def scrape_stats(driver):
    stats_dict = {
        'Expected_Goals_(xG)_Home': None,
        'Expected_Goals_(xG)_Host': None,
        'Ball_Possession_Home': None,
        'Ball_Possession_Host': None,
        'Goal_Attempts_Home': None,
        'Goal_Attempts_Host': None,
        'Shots_on_Goal_Home': None,
        'Shots_on_Goal_Host': None,
        'Shots_off_Goal_Home': None,
        'Shots_off_Goal_Host': None,
        'Blocked_Shots_Home': None,
        'Blocked_Shots_Host': None,
        'Free_Kicks_Home': None,
        'Free_Kicks_Host': None,
        'Corner_Kicks_Home': None,
        'Corner_Kicks_Host': None,
        'Offsides_Home': None,
        'Offsides_Host': None,
        'Throw-ins_Home': None,
        'Throw-ins_Host': None,
        'Goalkeeper_Saves_Home': None,
        'Goalkeeper_Saves_Host': None,
        'Fouls_Home': None,
        'Fouls_Host': None,
        'Red_Cards_Home': None,
        'Red_Cards_Host': None,
        'Yellow_Cards_Home': None,
        'Yellow_Cards_Host': None,
        'Total_Passes_Home': None,
        'Total_Passes_Host': None,
        'Completed_Passes_Home': None,
        'Completed_Passes_Host': None,
        'Tackles_Home': None,
        'Tackles_Host': None,
        'Crosses_Completed_Home': None,
        'Crosses_Completed_Host': None,
        'Interceptions_Home': None,
        'Interceptions_Host': None,
        'Attacks_Home': None,
        'Attacks_Host': None,
        'Dangerous_Attacks_Home': None,
        'Dangerous_Attacks_Host': None,
        'Distance_Covered_(km)_Home': None,
        'Distance_Covered_(km)_Host': None,
        'Clearances_Completed_Home': None,
        'Clearances_Completed_Host': None,
        'Pass_Success_per_Home': None,
        'Pass_Success_per_Host': None}
    
    cleaned_stats = []
    driver.implicitly_wait(2)
    try:
        stats_button = driver.find_element(By.XPATH, "//button[text()='Stats']")
        stats_button.click()
        stats = driver.find_elements(By.CLASS_NAME, 'wcl-category_ITphf')
        
        for stat in stats:
            stat = stat.text
            stat_split = stat.split('\n')
            current_stat = stat_split[1].replace(' ', '_')
            current_stat_home = current_stat + '_Home'
            current_stat_host = current_stat + '_Host'
            stats_dict[current_stat_home] = stat_split[0]
            stats_dict[current_stat_host] = stat_split[2]
    
    except NoSuchElementException:
        driver.implicitly_wait(3)
        pass
    return stats_dict


def scrape_summary(driver):

    home_goals_time = []
    home_current_score = []
    home_the_goal = []
    home_team_goals_assist = []
    home_yellow_time = []
    home_yellow_who = []
    home_yellow_why = []
    home_red_time = []
    home_red_who = []
    home_red_why = []
    home_substitution_time = []
    home_substitution_who = []
    home_substitution_with_who = []
    home_substitution_why = []
    
    away_goals_time = []
    away_current_score = []
    away_the_goal = []
    away_team_goals_assist = []
    away_yellow_time = []
    away_yellow_who = []
    away_yellow_why = []
    away_red_time = []
    away_red_who = []
    away_red_why = []
    away_substitution_time = []
    away_substitution_who = []
    away_substitution_with_who = []
    away_substitution_why = []
    driver.implicitly_wait(2)
    try:
        summary = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'smv__participantRow')))
    
        for index, summ in enumerate(summary):
            combined_info = None
            
            svg = WebDriverWait(summ, 3).until(
                EC.presence_of_element_located((By.TAG_NAME, "svg")))
            svg_class = svg.get_attribute('class')
            if svg_class == 'arrow arrowDown-ico':
                current_time  = summ.text.split('\n')[0]
                down = summ.text.split('\n')[1]
                up = summary[index+1].text.split('\n')[1]
                combined_info = f"{current_time} {up} {down}"
                
            summ_list = summ.text
            
            if 'smv__awayParticipant' in summ.get_attribute('class'):
                if combined_info is not None:
                    away_team_substitutions.append(combined_info)
                    
                handle_svg1(svg_class, summ_list,
                       away_goals_time,away_current_score,away_the_goal,away_team_goals_assist,
                       away_yellow_time,away_yellow_who,away_yellow_why,away_red_time,
                       away_red_who,away_red_why,away_substitution_time,away_substitution_who,
                       away_substitution_with_who,away_substitution_why)

            elif 'smv__homeParticipant' in summ.get_attribute('class'):

                if combined_info is not None:
                    home_team_substitutions.append(combined_info)
                    
                handle_svg1(svg_class, summ_list,home_goals_time ,home_current_score ,
                           home_the_goal,home_team_goals_assist ,home_yellow_time ,home_yellow_who ,home_yellow_why ,home_red_time ,
                           home_red_who ,home_red_why ,home_substitution_time ,home_substitution_who ,
                           home_substitution_with_who ,home_substitution_why)    
                
                
    except:
        driver.implicitly_wait(3)
        pass
        
    return {
        'home_goals_time': home_goals_time,
        'home_current_score': home_current_score,
        'home_the_goal': home_the_goal,
        'home_assist': home_team_goals_assist,
        'home_yellow_time': home_yellow_time,
        'home_yellow_who': home_yellow_who,
        'home_yellow_why': home_yellow_why,
        'home_red_time': home_red_time,
        'home_red_who': home_red_who,
        'home_red_why': home_red_why,
        'home_substitution_time': home_substitution_time,
        'home_substitution_who': home_substitution_who,
        'home_substitution_with_who': home_substitution_with_who,
        'home_substitution_why': home_substitution_why,
        
        'away_goals_time': away_goals_time,
        'away_current_score': away_current_score,
        'away_the_goal': away_the_goal,
        'away_assist': away_team_goals_assist,
        'away_yellow_time': away_yellow_time,
        'away_yellow_who': away_yellow_who,
        'away_yellow_why': away_yellow_why,
        'away_red_time': away_red_time,
        'away_red_who': away_red_who,
        'away_red_why': away_red_why,
        'away_substitution_time': away_substitution_time,
        'away_substitution_who': away_substitution_who,
        'away_substitution_with_who': away_substitution_with_who,
        'away_substitution_why': away_substitution_why
    }
    


def get_match_details(driver):
    match_details = {}
    try:
        # Check for and switch to match details frame if it exists
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        if frames:
            driver.switch_to.frame(frames[0])
        
        # Add longer wait time and better error handling
        wait = WebDriverWait(driver, 15)
        
        # Retry mechanism for getting match info
        retry_count = 3
        while retry_count > 0:
            try:
                match_info = wait.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'wcl-content_J-1BJ'))
                )
                
                # Process match details with better error handling
                full_text = " ".join([info.text.replace("\n", " ") for info in match_info])
                
                # Extract details with try-except for each field
                try:
                    match_details['referee'] = full_text.split("REFEREE:")[1].split("VENUE:")[0].strip() if "REFEREE:" in full_text else None
                    match_details['venue'] = full_text.split("VENUE:")[1].split("CAPACITY:")[0].strip() if "VENUE:" in full_text else None
                    match_details['capacity'] = full_text.split("CAPACITY:")[1].split("ATTENDANCE:")[0].strip() if "CAPACITY:" in full_text else None
                    match_details['attendance'] = full_text.split("ATTENDANCE:")[1].strip() if "ATTENDANCE:" in full_text else None
                except IndexError:
                    logger.warning("Error parsing match details text")
                break
                
            except (TimeoutException, StaleElementReferenceException) as e:
                retry_count -= 1
                if retry_count > 0:
                    logger.warning(f"Retrying match info extraction ({3-retry_count}/3)")
                    time.sleep(random.uniform(2, 4))
                else:
                    logger.error(f"Failed to extract match info after 3 attempts: {str(e)}")
        
        # Get stats with retry mechanism
        retry_count = 3
        while retry_count > 0:
            try:
                stats = scrape_stats(driver)
                match_details.update(stats)
                break
            except Exception as e:
                retry_count -= 1
                if retry_count > 0:
                    logger.warning(f"Retrying stats extraction ({3-retry_count}/3)")
                    time.sleep(random.uniform(2, 4))
                else:
                    logger.error(f"Failed to extract stats after 3 attempts: {str(e)}")
        
        # Get summary with retry mechanism
        retry_count = 3
        while retry_count > 0:
            try:
                summary = scrape_summary(driver)
                match_details.update(summary)
                break
            except Exception as e:
                retry_count -= 1
                if retry_count > 0:
                    logger.warning(f"Retrying summary extraction ({3-retry_count}/3)")
                    time.sleep(random.uniform(2, 4))
                else:
                    logger.error(f"Failed to extract summary after 3 attempts: {str(e)}")
        
        return match_details
    
    except Exception as e:
        logger.error(f"Error getting match details: {str(e)}")
        traceback.print_exc()
        return None
    finally:
        # Switch back to default content
        try:
            driver.switch_to.default_content()
        except:
            pass


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
