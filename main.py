import certifi
import ssl
import os
import sys
import zipfile
import shutil
import tempfile
import platform
############################################################
# main.py - Automates NISAR form population from Jira CAB issues using Selenium and robust ChromeDriver management.
#
# Features:
#   - Auto-downloads and matches ChromeDriver to installed Chrome version
#   - Fetches Jira issues and parses CAB description fields
#   - CLI-driven workflow for reviewing and populating NISAR forms
#   - Robust error handling, debug output, and field-level mapping
#
# Author: [Your Name]
# Date: [YYYY-MM-DD]
############################################################
import urllib.request
import json as pyjson

def get_latest_chromedriver(dest_dir=".chromedriver_cache"):
    """
    Download and extract the ChromeDriver matching the installed Chrome browser version for the current platform.
    Returns the path to chromedriver.exe. Handles cache cleanup and fallback to official archives if needed.
    """
    # Remove outdated ChromeDriver versions from cache (keep only current version)
    if os.path.isdir(dest_dir):
        for v in os.listdir(dest_dir):
            v_path = os.path.join(dest_dir, v)
            if os.path.isdir(v_path):
                # Only keep the current version (match_version or chrome_version)
                keep_version = False
                if 'chrome_version' in locals() and v == chrome_version:
                    keep_version = True
                if 'match_version' in locals() and v == match_version:
                    keep_version = True
                if not keep_version:
                    try:
                        print(f"[INFO] Removing outdated ChromeDriver cache: {v}")
                        shutil.rmtree(v_path)
                    except Exception as e:
                        print(f"[WARN] Failed to remove {v}: {e}")
    import subprocess
    # Detect platform and Chrome install location
    is_win = platform.system().lower().startswith("win")
    arch = platform.machine().lower()
    if is_win:
        plat_key = "win64" if "64" in arch else "win32"
        exe_name = "chromedriver.exe"
        chrome_path = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    else:
        plat_key = "linux64" if "linux" in platform.system().lower() else "mac-x64"
        exe_name = "chromedriver"
        chrome_path = "google-chrome"  # fallback for Linux/Mac

    # Get installed Chrome version (Windows: via win32api or PowerShell, else: CLI)
    chrome_version = None
    import re
    if is_win and os.path.exists(chrome_path):
        try:
            import win32api
            info = win32api.GetFileVersionInfo(chrome_path, '\\')
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            chrome_version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
        except ImportError:
            # Fallback: try to use powershell to get file version
            try:
                out = subprocess.check_output([
                    'powershell', '-Command', f"(Get-Item '{chrome_path}').VersionInfo.ProductVersion"
                ], stderr=subprocess.STDOUT, text=True)
                m = re.search(r'(\d+\.\d+\.\d+\.\d+)', out)
                if m:
                    chrome_version = m.group(1)
                else:
                    print(f"[WARN] Could not parse Chrome version from file properties: {out.strip()}")
            except Exception as e:
                print(f"[WARN] Could not get Chrome version from file properties: {e}")
    else:
        try:
            out = subprocess.check_output([chrome_path, "--version"], stderr=subprocess.STDOUT, text=True)
            chrome_version = out.strip().split()[-1]
        except Exception as e:
            print(f"[WARN] Could not get Chrome version: {e}")

    if not chrome_version:
        print("[WARN] Could not detect Chrome version, falling back to latest stable ChromeDriver.")
    else:
        print(f"[INFO] Detected Chrome version: {chrome_version}")

    # Download ChromeDriver version manifest JSON
    url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
    ssl_ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=ssl_ctx) as resp:
        data = pyjson.load(resp)

    # Find the best matching ChromeDriver version (search all versions, not just channels)
    match_version = None
    match_dl = None
    if chrome_version:
        chrome_major = chrome_version.split(".")[0]
        # Search all versions in the JSON (not just channels)
        # The JSON has a 'versions' key with all available versions
        all_versions = data.get("versions")
        if all_versions:
            for entry in all_versions:
                drv_version = entry["version"]
                drv_major = drv_version.split(".")[0]
                if drv_major == chrome_major:
                    for dl in entry["downloads"]["chromedriver"]:
                        if plat_key in dl["platform"]:
                            match_version = drv_version
                            match_dl = dl
                            break
                    if match_dl:
                        break
    # Fallback to latest stable if no match in JSON
    if not match_dl:
        stable = data["channels"]["Stable"]
        match_version = stable["version"]
        for dl in stable["downloads"]["chromedriver"]:
            if plat_key in dl["platform"]:
                match_dl = dl
                break

    # Fallback to official archive if still no match and we know the Chrome version
    if not match_dl and chrome_version:
        print(f"[INFO] Attempting to download ChromeDriver {chrome_version} from the official archive...")
        # Compose the archive URL
        archive_base = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing"
        archive_version = chrome_version
        archive_platform = plat_key
        # The archive uses e.g. .../148.0.7778.179/win64/chromedriver-win64.zip
        zip_name = f"chromedriver-{archive_platform}.zip"
        zip_url = f"{archive_base}/{archive_version}/{archive_platform}/{zip_name}"
        cache_dir = os.path.join(dest_dir, archive_version)
        chromedriver_path = os.path.join(cache_dir, exe_name)
        if os.path.exists(chromedriver_path):
            return chromedriver_path
        os.makedirs(cache_dir, exist_ok=True)
        zip_path = os.path.join(cache_dir, "chromedriver.zip")
        try:
            print(f"[INFO] Downloading ChromeDriver {archive_version} for {archive_platform} from archive...")
            with urllib.request.urlopen(zip_url, context=ssl_ctx) as resp, open(zip_path, 'wb') as out_file:
                shutil.copyfileobj(resp, out_file)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(cache_dir)
            for root, dirs, files in os.walk(cache_dir):
                if exe_name in files:
                    chromedriver_path = os.path.join(root, exe_name)
                    break
            print(f"[INFO] ChromeDriver ready at {chromedriver_path}")
            return chromedriver_path
        except Exception as e:
            print(f"[WARN] Could not download ChromeDriver {archive_version} from archive: {e}")
    if not match_dl:
        raise RuntimeError(f"No ChromeDriver download found for platform {plat_key}")

    # If we found a ChromeDriver but its version does not match the detected Chrome version, try the archive first
    if match_version and chrome_version and match_version.split('.')[0] != chrome_version.split('.')[0]:
        print(f"[INFO] ChromeDriver version from JSON ({match_version}) does not match Chrome version ({chrome_version}), trying archive...")
        archive_base = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing"
        archive_version = chrome_version
        archive_platform = plat_key
        zip_name = f"chromedriver-{archive_platform}.zip"
        zip_url = f"{archive_base}/{archive_version}/{archive_platform}/{zip_name}"
        cache_dir = os.path.join(dest_dir, archive_version)
        chromedriver_path = os.path.join(cache_dir, exe_name)
        if os.path.exists(chromedriver_path):
            return chromedriver_path
        os.makedirs(cache_dir, exist_ok=True)
        zip_path = os.path.join(cache_dir, "chromedriver.zip")
        try:
            print(f"[INFO] Downloading ChromeDriver {archive_version} for {archive_platform} from archive...")
            with urllib.request.urlopen(zip_url, context=ssl_ctx) as resp, open(zip_path, 'wb') as out_file:
                shutil.copyfileobj(resp, out_file)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(cache_dir)
            for root, dirs, files in os.walk(cache_dir):
                if exe_name in files:
                    chromedriver_path = os.path.join(root, exe_name)
                    break
            print(f"[INFO] ChromeDriver ready at {chromedriver_path}")
            return chromedriver_path
        except Exception as e:
            print(f"[WARN] Could not download ChromeDriver {archive_version} from archive: {e}")
    # Prepare cache dir and download from JSON as before
    cache_dir = os.path.join(dest_dir, match_version)
    chromedriver_path = os.path.join(cache_dir, exe_name)
    if os.path.exists(chromedriver_path):
        return chromedriver_path
    os.makedirs(cache_dir, exist_ok=True)
    zip_url = match_dl["url"]
    zip_path = os.path.join(cache_dir, "chromedriver.zip")
    print(f"[INFO] Downloading ChromeDriver {match_version} for {plat_key}...")
    with urllib.request.urlopen(zip_url, context=ssl_ctx) as resp, open(zip_path, 'wb') as out_file:
        shutil.copyfileobj(resp, out_file)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(cache_dir)
    for root, dirs, files in os.walk(cache_dir):
        if exe_name in files:
            chromedriver_path = os.path.join(root, exe_name)
            break
    print(f"[INFO] ChromeDriver ready at {chromedriver_path}")
    return chromedriver_path
############################################################
# Selenium field existence check utility (Edge/Chrome)
############################################################
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_xpath_fields(url, xpath_fields, driver_path="msedgedriver.exe", timeout=10):
    """
    Utility: Checks the existence of each XPath in xpath_fields on the given URL using Selenium.
    Prints the result for each field. (Edge version, not used in main workflow.)
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
    "Save Button": "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[4]/td/div/table/tbody/tr[1]/td/table/tbody/tr/td[3]/input"
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
        "User Impact": {"type": "parsed", "xpath_key": "User Impact"},
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
        # Support both 'Describe the Impact to Users' and 'Impact:'
        "Impact": r"(?:Describe the Impact to Users|Impact)[:：]?\s*([\s\S]*?)(?=Deployment Date:|Deployment From:|Deployment To:|Rollback Plan:|Roleback Plan:|Roleback:|$)",
        "User Impact": r"(?:Describe the Impact to Users|Impact)[:：]?\s*([\s\S]*?)(?=Deployment Date:|Deployment From:|Deployment To:|Rollback Plan:|Roleback Plan:|Roleback:|$)",
        "Deployment From": r"Deployment Date:[^\n]*\n•?\s*From[:：]?\s*([\d/\-]+)",
        "Deployment To": r"Deployment Date:[^\n]*\n[\s\S]*?•?\s*To[:：]?\s*([\d/\-]+)",
        "Roleback": r"Rollback Plan[:：]?\s*([\s\S]*?)(?=Communication to End Users:|Communication:|$)",
        "Communications": r"Communication to End Users[:：]?\s*([\s\S]*?)(?=CAB Presenter:|$)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, cab_text, re.IGNORECASE)
        if match:
            cab_data[key] = match.group(1).strip()
    # If User Impact is not found but Impact is, copy it
    if "User Impact" not in cab_data and "Impact" in cab_data:
        cab_data["User Impact"] = cab_data["Impact"]
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


def get_field_population_values(jira_issue):
    """
    Return a dict of {xpath: value} for the given Jira issue, using the mapping logic.
    """
    cab_desc_field = 'customfield_10916'
    cab_desc = jira_issue['fields'].get(cab_desc_field, '')
    cab_data = parse_cab_description(cab_desc)
    cab_id = jira_issue.get('key', '').strip()
    is_post = cab_id.upper() == 'POST'
    field_values = {}
    for map_key, mapping in JIRA_TO_XPATH_MAP.items():
        xpath_key = mapping['xpath_key']
        if map_key == 'Change Request Type Pre':
            value = not is_post
        elif map_key == 'Change Request Type Post':
            value = is_post
        elif mapping['type'] == 'direct':
            value = jira_issue['fields'].get(map_key, '')
        elif mapping['type'] == 'jira_key':
            value = jira_issue.get('key', '')
        elif mapping['type'] == 'parsed':
            value = cab_data.get(map_key, '')
        elif mapping['type'] == 'default':
            value = mapping.get('value', '')
        else:
            value = ''
        field_values[XPATH_FIELDS.get(xpath_key)] = value
    return field_values

def print_field_population_map(jira_issue):
    print("\n--- Field Population Map for First Jira Record ---")
    cab_desc_field = 'customfield_10916'
    cab_desc = jira_issue['fields'].get(cab_desc_field, '')
    cab_data = parse_cab_description(cab_desc)
    print(f"[DEBUG] CAB Description field: {cab_desc_field}")
    print(f"[DEBUG] CAB Description value: {cab_desc[:100]}{'...' if len(cab_desc) > 100 else ''}")
    cab_id = jira_issue.get('key', '').strip()
    is_post = cab_id.upper() == 'POST'
    for map_key, mapping in JIRA_TO_XPATH_MAP.items():
        xpath_key = mapping['xpath_key']
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

# --- Populate NISAR form fields using Selenium (no submit) ---
def populate_nisar_form(url, field_values, driver_path="msedgedriver.exe", timeout=10):
    """
    Uses Selenium to populate the NISAR form fields with the given values (no submit).
    Waits for user to review/submit, or allows skip/quit from CLI.
    """
    from selenium.common.exceptions import WebDriverException
    options = ChromeOptions()
    # options.add_argument("--headless")  # Run with visible browser window
    options.add_argument("--disable-gpu")
    chromedriver_path = get_latest_chromedriver()
    print(f"[DEBUG] Attempting to launch Chrome WebDriver at: {chromedriver_path}")
    try:
        service = ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        print("[DEBUG] Chrome WebDriver launched successfully.")
    except WebDriverException as e:
        print(f"[ERROR] Failed to launch Chrome WebDriver: {e}")
        return
    # Step 1: Go to CAB home page
    cab_home = "https://nisar.niaid.nih.gov/CAB/ManageCabReq.aspx"
    print(f"[DEBUG] Navigating to CAB home: {cab_home}")
    driver.get(cab_home)
    # Step 2: Click the button to open the form
    try:
        print("[DEBUG] Waiting for form launch button...")
        launch_btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[3]/div[2]/div[3]/table/tbody/tr[1]/td[1]/a[1]/img'))
        )
        launch_btn.click()
        print("[DEBUG] Form launch button clicked.")
    except Exception as e:
        print(f"[ERROR] Could not click form launch button: {e}")
        driver.quit()
        return
    # Step 3: Wait for the form to load (use the original form URL as a check)
    try:
        WebDriverWait(driver, timeout).until(EC.url_contains("CabReq.aspx"))
        print(f"[DEBUG] Form page loaded: {driver.current_url}")
    except Exception as e:
        print(f"[ERROR] Form page did not load: {e}")
        driver.quit()
        return
    print(f"\nChecking for required form fields at: {driver.current_url}\n")
    # Check for field existence after form is open
    missing_fields = []
    for field, xpath in XPATH_FIELDS.items():
        try:
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            print(f"[FOUND]   {field}")
        except Exception:
            print(f"[MISSING] {field}")
            missing_fields.append(field)
    if missing_fields:
        print(f"[ERROR] The following required fields are missing: {', '.join(missing_fields)}")
        driver.quit()
        return
    print(f"\nPopulating NISAR form fields at: {driver.current_url}\n")
    cr_id_prefix = None
    cr_id_full = None
    # Find CR ID value for later use
    for x, v in field_values.items():
        if x == XPATH_FIELDS.get("CR ID"):
            cr_id_full = str(v)
            if "-" in cr_id_full:
                cr_id_prefix = cr_id_full.split("-")[0]
            else:
                cr_id_prefix = cr_id_full
            break

    for xpath, value in field_values.items():
        if not xpath or value == '':
            print(f"[SKIPPED]   {xpath} (No value to populate)")
            continue
        try:
            elem = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            tag = elem.tag_name.lower()
            if tag == "input":
                input_type = elem.get_attribute("type")
                if input_type in ["text", "password", "number", "email", "date"]:
                    elem.clear()
                    elem.send_keys(str(value))
                elif input_type == "checkbox":
                    should_check = bool(value)
                    # Always try to set the checkbox state
                    if elem.is_selected() != should_check:
                        elem.click()
                    # Double-check and force with JS if needed
                    if elem.is_selected() != should_check:
                        driver.execute_script("arguments[0].checked = arguments[1];", elem, should_check)
                elif input_type == "radio":
                    # If value is True, always select this radio
                    if value is True or value == "True":
                        if not elem.is_selected():
                            elem.click()
                        # After selecting this radio, set Change Item Search to CR ID prefix
                        if xpath == XPATH_FIELDS.get("Change Type System") and cr_id_prefix:
                            try:
                                search_elem = WebDriverWait(driver, timeout).until(
                                    EC.presence_of_element_located((By.XPATH, XPATH_FIELDS.get("Change Item Search")))
                                )
                                search_elem.clear()
                                search_elem.send_keys(cr_id_prefix)
                                print(f"[POPULATED] {XPATH_FIELDS.get('Change Item Search')} <= {cr_id_prefix} (after radio select)")
                            except Exception as e:
                                print(f"[SKIPPED]   {XPATH_FIELDS.get('Change Item Search')} (after radio select, {e})")
                    # Otherwise, match by value string as before
                    elif elem.get_attribute("value") == str(value):
                        elem.click()
            elif tag == "textarea":
                elem.clear()
                elem.send_keys(str(value))
            elif tag == "div":
                # For content-editable divs
                if elem.get_attribute("contenteditable") == "true":
                    elem.clear()
                    elem.send_keys(str(value))
                else:
                    # Try to set innerText for non-contenteditable divs
                    driver.execute_script("arguments[0].innerText = arguments[1];", elem, str(value))
            else:
                print(f"[SKIPPED]   {xpath} (Unsupported tag: {tag})")
                continue
            print(f"[POPULATED] {xpath} <= {value}")
        except Exception as e:
            print(f"[SKIPPED]   {xpath} ({e})")
    print("\n[INFO] Fields populated. Please review the form in the browser.")
    # CLI prompt: continue (wait for submit), skip (close browser, skip), quit (close browser, exit)
    while True:
        user_input = input("[CLI] Press Enter to continue (wait for submit), 's' to skip this issue, or 'q' to quit: ").strip().lower()
        if user_input == 's':
            print("[INFO] Skipping this issue. Closing browser.")
            driver.quit()
            return 'skipped'
        elif user_input == 'q':
            print("[INFO] Quitting. Closing browser.")
            driver.quit()
            sys.exit(0)
        elif user_input == '':
            break
        else:
            print("[CLI] Invalid input. Please press Enter, 's', or 'q'.")
    # Wait for user to submit the form (detect by URL change or success element)
    print("[INFO] Waiting for form submission. The script will continue after you submit the form in the browser.")
    last_url = driver.current_url
    try:
        while True:
            if driver.current_url != last_url:
                print(f"[INFO] Detected navigation to {driver.current_url}")
                break
            import time
            time.sleep(2)
    except KeyboardInterrupt:
        print("[INFO] Interrupted by user. Closing browser.")
        driver.quit()
        return

    # Placeholder: Capture data from the successfully submitted page
    print("[TODO] Capture data from the submitted page here.")
    # Placeholder: Update Jira record
    print("[TODO] Update Jira record here.")
    driver.quit()
    return 'submitted'

def main():
    """
    Main entry point: Loads config, fetches Jira issues, filters, and processes each issue for NISAR form population.
    """
    config = load_config()
    nisar_url = config.get("nisar_form_url") or config.get("nisar_web_url") or config.get("nisar_url", "https://nisar.niaid.nih.gov/CAB/ManageCabReq.aspx")
    print("\nFetching issues from Jira...")
    issues = get_jira_issues(config)
    filtered_issues = [issue for issue in issues['issues'] if issue['fields'].get('status', {}).get('name', '').strip().lower() != 'ready to present']
    print(f"Found {len(filtered_issues)} issues (excluding 'Ready to Present').")
    import sys
    for idx, issue in enumerate(filtered_issues):
        print(f"\nProcessing Jira issue {idx+1}/{len(filtered_issues)}: {issue['key']} - {issue['fields']['summary']}")
        print_field_population_map(issue)
        field_values = get_field_population_values(issue)
        result = populate_nisar_form(nisar_url, field_values)
        if result == 'skipped':
            print(f"[INFO] Skipped issue {issue['key']}.")
            continue
        elif result == 'submitted':
            print(f"[INFO] Issue {issue['key']} processed.")
        else:
            print(f"[WARN] Issue {issue['key']} may not have been processed.")

if __name__ == "__main__":
    main()