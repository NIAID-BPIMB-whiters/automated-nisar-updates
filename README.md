# Automated NISAR Updates

This project automates the process of updating NISAR (NIAID Information Systems Architecture Repository) with data from Jira issues. It fetches CAB (Change Advisory Board) requests from a Jira filter, parses the structured CAB description fields, and fills out the NISAR web form using browser automation.

NISAR is hosted at https://nisar.niaid.nih.gov/CAB/ManageCabReq.aspx and requires access from the NIAID network or VPN.

## Features


## Prerequisites


## Installation

1. Clone the repository:
   ```

   # Automated NISAR Updates

   This project automates the process of updating NISAR (NIAID Information Systems Architecture Repository) with data from Jira CAB (Change Advisory Board) issues. It fetches CAB requests from a Jira filter, parses structured fields from the CAB Description, and fills out the NISAR web form using browser automation.

   NISAR is hosted at https://nisar.niaid.nih.gov/CAB/ManageCabReq.aspx and requires access from the NIAID network or VPN.

   ## Features

   - **Jira Integration**: Fetches issues from a specified Jira filter using REST API and PAT authentication.
   - **CAB Data Parsing**: Extracts structured fields from the Jira CAB Description custom field (e.g., Describe the Change, Business Owner, Deployment Date, etc.).
   - **Dynamic Field Mapping**: All field mappings and parsing logic are defined in `main.py` for easy review and extension.
   - **Pre/Post Logic**: The script determines the correct Change Request Type (Pre or Post) based on the CAB ID (Jira issue key). If the CAB ID is 'POST' (case-insensitive), the Post option is set to True and Pre to False; otherwise, Pre is True and Post is False.
   - **Status Filtering**: Jira issues with status 'Ready to Present' are automatically filtered out and not processed.
   - **Browser Automation**: Uses Selenium to check field existence and fill out the NISAR form.
   - **Configurable**: All URLs, credentials, and mappings are stored in `config.json`.

   ## Prerequisites

   - Python 3.7+
   - Access to NIAID VPN or network for NISAR access
   - Google Chrome browser (auto-managed ChromeDriver)
   - Jira Personal Access Token (PAT)

   ## Installation

   1. Clone the repository:
      ```
      git clone https://github.com/yourusername/automated-nisar-updates.git
      cd automated-nisar-updates
      ```

   2. Install dependencies:
      ```
      pip install -r requirements.txt
      ```

   3. Ensure VPN connection for NISAR access.

   4. Configure `config.json` with your Jira PAT and other settings.

   ## Usage

   Run the script to process Jira issues and update NISAR:

   ```
   python main.py
   ```

   The script will:
   - Fetch issues from the configured Jira filter.
   - Filter out issues with status 'Ready to Present'.
   - Parse the CAB Description field for each issue.
   - Print a field population map for each eligible Jira record, showing exactly what will be set for each NISAR form field.
   - Open the NISAR form in Chrome, populate all mapped fields, and wait for user review/submit (no auto-submit).

   **Note:** The script does not submit the form automatically. You must review and submit each form manually in the browser window.

   ## Configuration

   Edit `config.json` to customize:

   - `jira_url`: Jira base URL
   - `jira_pat`: Your Personal Access Token
   - `jira_filter_url`: URL of the Jira filter to fetch issues
   - `nisar_web_url`: NISAR management page URL
   - `nisar_form_url`: NISAR form URL
   - `presenter_branch`: Branch for CAB presenter lookup
   - `cab_field`: Jira custom field ID for CAB description (should be `customfield_10916`)

   ## How It Works

   1. **Fetch Jira Data**: Queries the Jira API for issues matching the filter.
   2. **Filter Issues**: Excludes any issue with status 'Ready to Present'.
   3. **Parse CAB Fields**: Extracts key-value pairs from the CAB Description using regex patterns for known field headers.
   4. **Determine Pre/Post**: Sets Change Request Type Pre/Post based on the CAB ID (Jira issue key).
   5. **Print Mapping**: Prints a field population map for review.
   6. **Automate NISAR**: Opens the NISAR form, populates all mapped fields, and waits for user review/submit.

   ## Project Structure

   - `main.py`: Main script for Jira fetching, CAB parsing, and NISAR automation.
   - `config.json`: Configuration file (ignored by Git for security).
   - `requirements.txt`: Python dependencies.
   - `.chromedriver_cache/`: ChromeDriver cache (auto-managed).
   - `.gitignore`: Excludes sensitive files from version control.
   - `README.md`: This file.

   ## License

   This project is licensed under the MIT License.