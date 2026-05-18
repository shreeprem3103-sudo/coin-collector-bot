import os
import re
import json
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By

# --- 1. CONFIGURATION ---
PACKAGE_NAME = "com.elections.india"
PASSWORD_DATA = "31032008"
DOMAIN_DATA = "@jieluv.com"
PROGRESS_FILE = "bot_progress.json"

BASE_SCREEN_WIDTH = 720.0
BASE_SCREEN_HEIGHT = 1600.0

COORDINATES = {
    "play": (348.5, 1354.1),
    "email": (378.5, 343.7),
    "password": (412.3, 414.7),
    "signin": (418.3, 501.7),
    "click_5": (102.9, 772.5),
    "click_6": (359.5, 1165.3),
    "click_7": (614.0, 527.7),
    "click_8": (248.6, 732.5),
    "click_9": (618.0, 720.5),
    "click_10": (248.6, 918.4),
    "click_11": (603.2, 927.4),
    "click_12": (258.6, 1113.3),
    "click_13": (624.0, 1113.3),
    "click_14": (71.9, 105.9),
    "click_15": (663.0, 117.9),
    "final_click": (357.5, 1391.0)
}

# --- 2. SETUP APP RUNNER ---
options = UiAutomator2Options()
options.platform_name = "Android"
options.automation_name = "UiAutomator2"
options.device_name = "Android Emulator"
options.app = "./game.apk"
options.app_package = PACKAGE_NAME
options.no_reset = False

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
time.sleep(12)

window_size = driver.get_window_size()
SCALE_X = window_size['width'] / BASE_SCREEN_WIDTH
SCALE_Y = window_size['height'] / BASE_SCREEN_HEIGHT

def click_coord(key):
    orig_x, orig_y = COORDINATES[key]
    driver.tap([(int(orig_x * SCALE_X), int(orig_y * SCALE_Y))], 100)
    time.sleep(1.2)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f).get("last_index", 57)
    return 57

def save_progress(current_idx):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({"last_index": current_idx}, f)

# --- 3. DYNAMIC MATH CRACKER ---
def solve_and_click_captcha():
    """Reads visible text math problem and selects the matching option element dynamically"""
    try:
        # Find any text element containing addition or subtraction operators
        math_elements = driver.find_elements(By.XPATH, "//*[contains(@text, '+') or contains(@text, '-')]")
        if not math_elements:
            print("Math problem text element not detected on current interface layout.")
            return False
            
        problem_text = math_elements[0].text
        print(f"Captured Problem Text: {problem_text}")
        
        # Clean string layout and extract mathematical expression
        clean_equation = re.sub(r'[^0-9\+\-\*\/]', '', problem_text)
        if not clean_equation:
            return False
            
        correct_answer = str(eval(clean_equation))
        print(f"Calculated Numerical Solution Target: {correct_answer}")
        
        # Scan the layout tree for the specific text element that matches our calculated answer
        target_option_button = driver.find_elements(By.XPATH, f"//*[@text='{correct_answer}']")
        
        if target_option_button:
            target_option_button[0].click()
            print(f"Success: Clicked on-screen choice element containing text value: {correct_answer}")
            return True
        else:
            print(f"Could not locate an explicit text element choice matching: {correct_answer}")
            return False
    except Exception as e:
        print(f"Dynamic captcha solver process error: {e}")
        return False

# --- 4. ENGINE TASK LOOP ---
start_index = load_progress()

for account_idx in range(start_index, start_index + 100):
    current_email = f"{account_idx}{DOMAIN_DATA}"
    print(f"Initiating process thread for target account: {current_email}")
    
    try:
        click_coord("play")
        
        # Enter credentials natively via ADB shell integration
        driver.tap([(int(COORDINATES["email"][0]*SCALE_X), int(COORDINATES["email"][1]*SCALE_Y))], 100)
        os.system(f"adb shell input text '{current_email}'")
        time.sleep(1)
        
        driver.tap([(int(COORDINATES["password"][0]*SCALE_X), int(COORDINATES["password"][1]*SCALE_Y))], 100)
        os.system(f"adb shell input text '{PASSWORD_DATA}'")
        time.sleep(1)
        
        click_coord("signin")
        time.sleep(7)
        
        # Handle structural fast navigation layout triggers
        for i in range(5, 14):
            click_coord(f"click_{i}")
            
        time.sleep(3)
        click_coord("click_14")
        click_coord("click_15")
        time.sleep(5) # Wait for captcha popup to completely paint onto layout viewport
        
        # Run dynamic script solver engine
        solve_and_click_captcha()
        time.sleep(2)
        
        click_coord("final_click")
        
        save_progress(account_idx + 1)
        
        # Restart application container context for clean session handoff
        driver.terminate_app(PACKAGE_NAME)
        driver.activate_app(PACKAGE_NAME)
        time.sleep(5)
        
    except Exception as error:
        print(f"Error handling task structure for row {account_idx}: {error}")
        save_progress(account_idx + 1)
        driver.terminate_app(PACKAGE_NAME)
        driver.activate_app(PACKAGE_NAME)
        continue

driver.quit()
