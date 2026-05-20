# --- Selenium field existence check ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_xpath_fields(url, xpath_fields, driver_path="msedgedriver.exe", timeout=10):
    """
    Checks the existence of each XPath in xpath_fields on the given URL.
    Prints the result for each field.
    """
    options = EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    service = EdgeService(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)
    driver.get(url)
    print(f"\nChecking field existence on: {url}\n")
    for field, xpath in xpath_fields.items():
        try:
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            print(f"[FOUND]   {field}")
        except (NoSuchElementException, TimeoutException):
            print(f"[MISSING] {field}")
    driver.quit()

# ===============================
# XPATH FIELD CAPTURE SECTION
# ===============================
# Use this section to document/capture all XPath values for fields that need to be updated in the NISAR form.
# Example:
# XPATH_FIELDS = {
#     "Title": "//input[@id='title']",
#     "Business Owner": "//input[@id='business_owner']",
#     ...
# }
#
XPATH_FIELDS = {
    # "Field Name": "XPath Value",
    "Title": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[2]/td[2]/input",
    "Change Type System": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[4]/td[2]/span[1]/input",
    "Change Item Search": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[5]/td[2]/table/tbody/tr[1]/td/input",
    "Change Item Select": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[5]/td[2]/table/tbody/tr[2]/td[2]",
    "Add Change Item Button": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[5]/td[2]/table/tbody/tr[2]/td[2]/img[1]",
    "Change Request Type Pre": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[5]/td[2]/table/tbody/tr[2]/td[2]/img[1]",
    "Change Request Type Post": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[6]/td[2]/span[2]/input",
    "OCICB Requester": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[7]/td[2]/input",
    "Describe the Change": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[9]/td[2]/div[1]/table/tbody/tr[3]/td/div",
    "Category Environment Setup": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[10]/td[2]/div/div/ul/li[3]/ul/li[1]/div/label/input",
    "Category Minor Release": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[10]/td[2]/div/div/ul/li[3]/ul/li[2]/div/label/input",
    "Category New System": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[10]/td[2]/div/div/ul/li[3]/ul/li[3]/div/label/input",
    "Category System Decommission": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[10]/td[2]/div/div/ul/li[3]/ul/li[4]/div/label/input",
    "Category Version Upgrade": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[10]/td[2]/div/div/ul/li[3]/ul/li[5]/div/label/input",
    "Category Password": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[10]/td[2]/div/div/ul/li[5]/ul/li[1]/div/label/input",
    "Category Security Vulnarability": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[10]/td[2]/div/div/ul/li[5]/ul/li[2]/div/label/input",
    "Category SSL": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[10]/td[2]/div/div/ul/li[5]/ul/li[3]/div/label/input",
    "Category Ops Maint": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[10]/td[2]/div/div/ul/li[6]/ul/li[2]/div/label/input",
    "Why Change": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[12]/td[2]/div[1]/table/tbody/tr[3]/td/div",
    "Stakeholders": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[13]/td[2]/input",
    "Number of Users": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[14]/td[2]/input",
    "User Impact": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[15]/td[2]/div[1]/table/tbody/tr[3]/td/div",
    "Deployment From": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[16]/td[2]/input[1]",
    "Deployment To": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[16]/td[2]/input[2]",
    "Time Frame": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[16]/td[2]/input[3]",
    "During hours no": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[17]/td[2]/span[2]/input",
    "Downtime No": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[18]/td[2]/span[2]/input",
    "Deploy type manual": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[20]/td[2]/span[1]/input",
    "CR ID": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[21]/td[2]/input",
    "Roleback": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[23]/td[2]/div[1]/table/tbody/tr[3]/td/div",
    "Communications": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[2]/td/div/table/tbody/tr[24]/td[2]/div[1]/table/tbody/tr[3]/td/div",
    #"Save Button": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[4]/td/div/table/tbody/tr[1]/td/table/tbody/tr/td[3]/input"
}
# ===============================

# JIRA TO XPATH FIELD MAPPING SECTION
# ===============================
# Use this section to map Jira record fields/attributes to the corresponding XPATH_FIELDS keys.
# Specify whether the mapping is direct (from a Jira field) or parsed (from a CAB Description attribute).
#
# Example:
# JIRA_TO_XPATH_MAP = {
#     "jira_field_or_cab_attribute": {"type": "direct"|"parsed"|"default", "xpath_key": "XPATH_FIELDS_key", "value": ...},
#     ...
# }
JIRA_TO_XPATH_MAP = {
    # Direct mappings from Jira fields
        "summary": {"type": "direct", "xpath_key": "Title"},
        "key": {"type": "jira_key", "xpath_key": "CR ID"},
        "Stakeholders": {"type": "parsed", "xpath_key": "Stakeholders"},
        "Number of Users": {"type": "parsed", "xpath_key": "Number of Users"},
        "Describe the Change": {"type": "parsed", "xpath_key": "Describe the Change"},
        "Why Change": {"type": "parsed", "xpath_key": "Why Change"},
        "Impact": {"type": "parsed", "xpath_key": "Impact"},
        "Deployment From": {"type": "parsed", "xpath_key": "Deployment From"},
        "Deployment To": {"type": "parsed", "xpath_key": "Deployment To"},
        "Roleback": {"type": "parsed", "xpath_key": "Roleback"},
        "Communications": {"type": "parsed", "xpath_key": "Communications"},
    # Set/default values (static)
    "Time Frame": {"type": "default", "xpath_key": "Time Frame", "value": "after hours"},
    "Change Type System": {"type": "default", "xpath_key": "Change Type System", "value": True},
    "Deploy type manual": {"type": "default", "xpath_key": "Deploy type manual", "value": True},
    "During hours no": {"type": "default", "xpath_key": "During hours no", "value": True},
    "Downtime No": {"type": "default", "xpath_key": "Downtime No", "value": True},
    # Categories set by other logic (e.g. based on keywords in CAB Description or Jira fields)
    "Category Environment Setup": {"type": "default", "xpath_key": "Category Environment Setup", "value": False},
    "Category Minor Release": {"type": "default", "xpath_key": "Category Minor Release", "value": False},
    "Category New System": {"type": "default", "xpath_key": "Category New System", "value": False},
    "Category System Decommission": {"type": "default", "xpath_key": "Category System Decommission", "value": False},
    "Category Version Upgrade": {"type": "default", "xpath_key": "Category Version Upgrade", "value": False},
    "Category Password": {"type": "default", "xpath_key": "Category Password", "value": False},
    "Category Security Vulnerability": {"type": "default", "xpath_key": "Category Security Vulnerability", "value": False},
    "Category SSL": {"type": "default", "xpath_key": "Category SSL", "value": False},
    "Category Ops Maint": {"type": "default", "xpath_key": "Category Ops Maint", "value": False},
    # Set by other logic (jira issue status)
    "Change Request Type Pre": {"type": "default", "xpath_key": "Change Request Type Pre", "value": True},
    "Change Request Type Post": {"type": "default", "xpath_key": "Change Request Type Post", "value": False},
}

# ===============================

# Helper to parse CAB Description for attributes
def parse_cab_description(cab_text):
    """
    Extracts key-value pairs from the CAB Description field.
    Returns a dict: {attribute: value, ...}
    """
    import re
    cab_data = {}
    if not cab_text:
        return {}

    # Patterns for each field
    patterns = {
        "Describe the Change": r"Describe the Change[:：]?\s*([\s\S]*?)(?=Why we are making these changes:|Why we are making these changes：|Why Change:|Why Change：|$)",
        "Why Change": r"Why (?:we are making these changes|Change)[:：]?\s*([\s\S]*?)(?=Business Owner:|Number of Users:|Describe the Impact to Users:|Impact:|$)",
        "Stakeholders": r"Business Owner[:：]?\s*(.*)",
        "Number of Users": r"Number of Users[:：]?\s*(\d+)",
        "Impact": r"Describe the Impact to Users[:：]?\s*([\s\S]*?)(?=Deployment Date:|Deployment From:|Deployment To:|Rollback Plan:|Roleback Plan:|Roleback:|$)",
        "Deployment From": r"Deployment Date:[^\n]*\n•?\s*From[:：]?\s*([\d/\-]+)",
        "Deployment To": r"Deployment Date:[^\n]*\n[\s\S]*?•?\s*To[:：]?\s*([\d/\-]+)",
        "Roleback": r"Rollback Plan[:：]?\s*([\s\S]*?)(?=Communication to End Users:|Communication:|$)",
        "Communications": r"Communication to End Users[:：]?\s*([\s\S]*?)(?=CAB Presenter:|$)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, cab_text, re.IGNORECASE)
        if match:
            cab_data[key] = match.group(1).strip()
    return cab_data
# ===============================

# NISAR Jira Issue Fetcher (Starter)
# This script fetches issues from Jira and prints their keys and summaries.
import json
import requests

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def get_jira_issues(config):
    headers = {
        'Authorization': f'Bearer {config["jira_pat"]}',
        'Content-Type': 'application/json'
    }
    filter_id = config["jira_filter_url"].split('filter=')[1]
    url = f'{config["jira_url"].rstrip("/")}/rest/api/2/search?jql=filter={filter_id}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch Jira issues: {response.status_code} - {response.text}")


def print_field_population_map(jira_issue):
    """
    Print what value would be set for each form field for the given Jira issue.
    """
    print("\n--- Field Population Map for First Jira Record ---")
    # CAB Description is a custom Jira attribute (update the field name as needed)
    cab_desc_field = 'customfield_10916'  # <-- Updated to correct CAB Description field
    cab_desc = jira_issue['fields'].get(cab_desc_field, '')
    cab_data = parse_cab_description(cab_desc)
    print(f"[DEBUG] CAB Description field: {cab_desc_field}")
    print(f"[DEBUG] CAB Description value: {cab_desc[:100]}{'...' if len(cab_desc) > 100 else ''}")
    # Determine Change Request Type Pre/Post based on CAB ID (CR ID)
    cab_id = jira_issue.get('key', '').strip()
    is_post = cab_id.upper() == 'POST'
    for map_key, mapping in JIRA_TO_XPATH_MAP.items():
        xpath_key = mapping['xpath_key']
        # Special logic for Change Request Type Pre/Post
        if map_key == 'Change Request Type Pre':
            value = not is_post
        elif map_key == 'Change Request Type Post':
            value = is_post
        elif mapping['type'] == 'direct':
            value = jira_issue['fields'].get(map_key, '[NOT FOUND]')
        elif mapping['type'] == 'jira_key':
            value = jira_issue.get('key', '[NOT FOUND]')
        elif mapping['type'] == 'parsed':
            value = cab_data.get(map_key, '[NOT FOUND]')
        elif mapping['type'] == 'default':
            value = mapping.get('value', '[NO DEFAULT]')
        else:
            value = '[UNKNOWN TYPE]'
        print(f"{xpath_key:30} <= {map_key:25} : {value}")

def main():
    config = load_config()
    # Check for field existence on the NISAR form page
    nisar_url = config.get("nisar_form_url") or config.get("nisar_web_url")
    if nisar_url:
        check_xpath_fields(nisar_url, XPATH_FIELDS)
    else:
        print("NISAR form URL not found in config.json. Skipping field existence check.")
    # Fetch Jira issues
    print("\nFetching issues from Jira...")
    issues = get_jira_issues(config)
    # Filter out issues with status 'Ready to Present'
    filtered_issues = [issue for issue in issues['issues'] if issue['fields'].get('status', {}).get('name', '').strip().lower() != 'ready to present']
    print(f"Found {len(filtered_issues)} issues (excluding 'Ready to Present').")
    for issue in filtered_issues:
        print(f"{issue['key']}: {issue['fields']['summary']}")
    # Print field population map for the first Jira record
    if filtered_issues:
        print_field_population_map(filtered_issues[0])

if __name__ == "__main__":
    main()