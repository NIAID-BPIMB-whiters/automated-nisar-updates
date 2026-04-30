import json
import requests
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert

CAB_KEYWORDS = [
    "Describe the Change:",
    "Why we are making these changes:",
    "Business Owner:",
    "Number of Users:",
    "Describe the Impact to Users:",
    "Deployment Date:",
    "Rollback Plan:",
    "Communication to End Users:",
    "CAB Presenter:"
]

# Placeholder field mappings - update with actual IDs/XPaths from inspecting the NISAR form
FIELD_MAPPING = {
    "Summary": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[2]/td[2]/input",  # XPath for Jira summary
    "System Radio Button": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[4]/td[2]/span[1]/input",  # XPath for system radio button"Describe the Change": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[9]/td[2]/div[1]/table/tbody/tr[3]/td/div",  # Update with actual ID
    "Why we are making these changes": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[12]/td[2]/div[1]/table/tbody/tr[3]/td/div",  # Update
    "Business Owner": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[13]/td[2]/input",  # Update
    "Number of Users": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[14]/td[2]/input",  # Update
    "Describe the Impact to Users": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[15]/td[2]/div[1]/table/tbody/tr[3]/td/div",  # Update
    "Deployment Date": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[16]/td[2]/input[1]",  # Update - may need separate From/To
    "Rollback Plan": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[23]/td[2]/div[1]/table/tbody/tr[3]/td/div",  # Update
    "Communication to End Users": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[24]/td[2]/div[1]/table/tbody/tr[3]/td/div",  # Update
    "CAB Presenter": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[7]/td[2]/input",  # Update  
    "Post-Implementation Radio Button": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[6]/td[2]/span[2]/input",  # XPath for post-implementation radio button
    "Search Field": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[5]/td[2]/table/tbody/tr[1]/td/input",  # XPath for search field
    "System Select": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[5]/td[2]/table/tbody/tr[2]/td[1]/select[1]",  # XPath for system select
    "Add Button": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[5]/td[2]/table/tbody/tr[2]/td[2]/img[1]"  # XPath for add button
}

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def get_jira_issues(config):
    headers = {
        'Authorization': f'Bearer {config["jira_pat"]}',
        'Content-Type': 'application/json'
    }
    # Extract filter ID from URL
    filter_id = config["jira_filter_url"].split('filter=')[1]
    url = f'{config["jira_url"].rstrip("/")}/rest/api/2/search?jql=filter={filter_id}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch Jira issues: {response.status_code} - {response.text}")

def parse_cab_description(text):
    data = {}
    for i, kw in enumerate(CAB_KEYWORDS):
        start = text.find(kw)
        if start == -1:
            continue
        start += len(kw)
        end = text.find(CAB_KEYWORDS[i+1]) if i+1 < len(CAB_KEYWORDS) else len(text)
        data[kw.strip(":")] = text[start:end].strip()
    return data

def submit_to_nisar(config, cab_data):
    # Test navigation to NISAR form using Edge
    from selenium.webdriver import EdgeOptions
    options = EdgeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    service = EdgeService(executable_path="msedgedriver.exe")
    driver = webdriver.Edge(service=service, options=options)
    try:
        print("Opening Edge browser and navigating to NISAR main page...")
        driver.get(config["nisar_web_url"])
        print("Navigated to NISAR main page.")
        # Wait a bit
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Main page loaded.")
        # Click the NEW CAB REQUEST button
        button_xpath = "/html/body/form/div[3]/div[2]/div[3]/table/tbody/tr[1]/td[1]/a[1]/img"
        try:
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
            button.click()
            print("Clicked NEW CAB REQUEST button.")
        except Exception as e:
            print(f"Could not click button: {e}")
            # Fallback: navigate directly to form
            driver.get(config["nisar_form_url"])
            print("Fallback: Navigated directly to form.")
        
        print("Now on NISAR form.")
        # Check for errors
        page_source = driver.page_source
        if "500" in page_source or "Internal Server Error" in page_source:
            print("Detected 500 Internal Server Error on the page.")
        elif "404" in page_source or "Not Found" in page_source:
            print("Detected 404 Not Found error.")
        elif "403" in page_source or "Forbidden" in page_source:
            print("Detected 403 Forbidden error.")
        else:
            print("Page loaded successfully. No obvious errors detected.")
        # Placeholder for form filling
        # Wait for page load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Page body loaded.")
        # Fill the form with CAB data in specific order
        fill_order = [
            "Summary",
            "System Radio Button",
            "Search Field",
            "Post-Implementation Radio Button",
            "System Select",
            "Add Button",
            "Describe the Change",
            "Why we are making these changes",
            "Business Owner",
            "Number of Users",
            "Describe the Impact to Users",
            "Deployment Date",
            "Rollback Plan",
            "Communication to End Users",
            "CAB Presenter"
        ]
        print("Filling the form...")
        for key in fill_order:
            value = cab_data.get(key, "")
            field_locator = FIELD_MAPPING.get(key)
            if field_locator:
                try:
                    if field_locator.startswith('/'):
                        # Use XPath
                        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, field_locator)))
                    else:
                        # Use ID
                        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, field_locator)))
                    if element.tag_name == 'select':
                        select = Select(element)
                        options = select.options
                        if len(options) == 1:
                            select.select_by_index(0)
                            print(f"Selected {key}")
                        else:
                            print(f"Multiple options for {key}, manual entry needed")
                    elif element.tag_name in ['input', 'img'] and element.get_attribute('type') in ['radio', 'checkbox', None]:
                        element.click()
                        print(f"Clicked {key}")
                    elif value != "":  # Fill text fields if value is set
                        element.clear()
                        element.send_keys(value)
                        print(f"Filled {key}")
                    else:
                        print(f"Skipped {key} (no value)")
                except Exception as e:
                    print(f"Could not fill {key}: {e}")
            else:
                print(f"No mapping for {key}")
        # Handle any alerts
        try:
            Alert(driver).accept()
            print("Accepted alert")
        except:
            pass
        # Submit the form (update with actual submit button ID)
        try:
            submit_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "btnSubmit")))  # Update with actual ID
            submit_button.click()
            print("Form submitted.")
        except Exception as e:
            print(f"Could not submit form: {e}")
        # Wait for confirmation or something
        time.sleep(2)
    except Exception as e:
        print(f"Error in NISAR submission: {e}")
    finally:
        input("Press Enter to close browser...")
        driver.quit()

def main():
    try:
        config = load_config()
        print("Testing Jira connection...")
        issues = get_jira_issues(config)
        print(f"Successfully retrieved {issues['total']} issues from Jira.")
        # Process each issue (limit to first for testing)
        for issue in issues['issues'][:1]:
            print(f"Processing Issue: {issue['key']} - {issue['fields']['summary']}")
            status = issue['fields']['status']['name']
            print(f"Issue Status: {status}")
            cab_field = issue['fields'].get(config.get('cab_field', 'customfield_10916'), '')
            if cab_field:
                cab_data = parse_cab_description(cab_field)
                cab_data["Summary"] = issue['fields']['summary']  # Add summary to data
                # Select radio button based on status
                if status == "Add to NISAR":
                    cab_data["System Radio Button"] = ""  # Select system radio button
                else:
                    cab_data["Post-Implementation Radio Button"] = ""  # Select post-implementation radio button
                prefix = issue['key'].split('-')[0]  # First part of issue key
                cab_data["Search Field"] = prefix  # Fill search with prefix
                cab_data["System Select"] = ""  # Placeholder for select
                cab_data["Add Button"] = ""  # Placeholder for add button
                print("CAB Data:", cab_data)
                # Submit to NISAR
                submit_to_nisar(config, cab_data)
            print("---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()