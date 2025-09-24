"""
    项目简介:
        北大燕园月饼半自动预定脚本(半自动指完成用户登录，选购月饼，完成下单。由此实现了锁定订单，最后需要手动去完成后续环节，如添加手机号，与支付)
    使用方案:
        1. 安装依赖 pip install selenium webdriver-manager
        2. 修改 USERNAME 和 PASSWORD 变量为你的登录信息
        3. 在main()选择购置"燕园皓月"或"燕园秋月",或者两者都选
        4. 在对应函数中，确认订购份数。若只需要订购一份，则无需变动代码。若需要增加份数，如订购两份燕园皓月，则将
            var item = vm.list[0];  // 燕园皓月 (index 0)
            vm.add(item, 1);  // 调用 add
            return { success: true, number: item.number, total: vm.totalnum };
            
            修改为
            
            var item = vm.list[0];  // 燕园皓月 (index 0)
            vm.add(item, 1);  // 调用 add
            vm.add(item, 1);  // 第二次调用 add
            return { success: true, number: item.number, total: vm.totalnum };
            
        5. 运行脚本 python mooncake.py (请于11:00之前运行脚本，以尽早完成程序启动与用户登录阶段。程序会自动在11:00时进行订购与下单)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime

# Configuration
URL = "https://yanyuan.pku.edu.cn/yywd/wap/default/index"
USERNAME = "your_username"  # Replace with your actual username if different
PASSWORD = "your_password"  # Replace with your actual password if different

def setup_driver():
    """Set up Chrome WebDriver with webdriver-manager."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Maximize window
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login(driver):
    """Handle login process."""
    wait = WebDriverWait(driver, 10)
    driver.get(URL)
    
    try:
        # Wait for and fill username field
        username_field = wait.until(EC.presence_of_element_located((By.ID, "user_name")))
        username_field.clear()
        username_field.send_keys(USERNAME)
        
        # Wait for and fill password field
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_field.clear()
        password_field.send_keys(PASSWORD)
        
        # Check if captcha is present
        try:
            captcha_field = wait.until(EC.presence_of_element_located((By.ID, "valid_code")))
            if captcha_field.is_displayed():
                print("Captcha detected. Please enter the captcha manually in the browser and press Enter here to continue...")
                input()  # Pause for manual captcha input
        except TimeoutException:
            print("No captcha detected, proceeding...")
        
        # Click login button
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "logon_button")))
        login_button.click()
        
        # Wait for login to complete (adjust selector to an element that appears after successful login)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "header")))  # Replace with actual post-login element class
        print("Login successful!")
        
    except TimeoutException as e:
        print("Login timed out. Check selectors or page structure.")
        print("Error:", e)
        driver.quit()
        exit(1)

def add_yanyuan_haoyue(driver):
    wait = WebDriverWait(driver, 20)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list")))
        
        # 执行 JS 获取 Vue 实例并调用 add
        script = """
        var vm = document.getElementById('app').__vue__;
        if (vm && vm.list.length > 1) {
            var item = vm.list[0];  // 燕园皓月 (index 0)
            vm.add(item, 1);  // 调用 add
            return { success: true, number: item.number, total: vm.totalnum };
        } else {
            return { success: false, error: 'Vue instance or list not ready' };
        }
        """
        result = driver.execute_script(script)
        print("加购结果:", result)
        
        if result['success']:
            print(f"燕园秋月数量增加至 {result['number']}")
        else:
            print("加购失败:", result['error'])
    except Exception as e:
        print(f"加购失败: {e}")
        
def add_yanyuan_qiuyue(driver):
    wait = WebDriverWait(driver, 20)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list")))
        
        # 执行 JS 获取 Vue 实例并调用 add
        script = """
        var vm = document.getElementById('app').__vue__;
        if (vm && vm.list.length > 1) {
            var item = vm.list[1];  // 燕园秋月 (index 1)
            vm.add(item, 1);  // 调用 add
            return { success: true, number: item.number, total: vm.totalnum };
        } else {
            return { success: false, error: 'Vue instance or list not ready' };
        }
        """
        result = driver.execute_script(script)
        print("加购结果:", result)
        
        if result['success']:
            print(f"燕园秋月数量增加至 {result['number']}")
        else:
            print("加购失败:", result['error'])   
    except Exception as e:
        print(f"加购失败: {e}")

def wait_for_noon():
    """Wait until 11:00:00 (noon) of the current day with dynamic sleep intervals."""
    print("Checking current time...")
    while True:
        now = datetime.now()
        if now.hour == 11 and now.minute == 0 and now.second == 0:
            print("Reached 11:00:00, proceeding with add operation...")
            break
        remaining_seconds = ((11 - now.hour) * 3600) + ((0 - now.minute) * 60) - now.second
        if remaining_seconds > 0:
            # Dynamic sleep based on remaining time
            if remaining_seconds > 600:  # More than 10 minutes
                sleep_time = 10
            elif remaining_seconds > 60:  # 1-10 minutes
                sleep_time = 1
            elif remaining_seconds > 10:  # 10-60 seconds
                sleep_time = 0.5
            else:  # Less than 10 seconds
                sleep_time = 0.01
            print(f"Current time: {now.strftime('%H:%M:%S')}, waiting {remaining_seconds} seconds until 11:00:00, sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
        else:
            print("Current time is past 11:00, proceeding immediately...")
            break

def main():
    driver = setup_driver()
    try:
        login(driver)
        wait_for_noon()
        add_yanyuan_qiuyue(driver)
        # add_yanyuan_haoyue(driver)
        driver.execute_script("document.getElementById('app').__vue__.save();")
        input("Press Enter to close the browser...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()