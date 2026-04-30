# Automated NISAR Updates

This project automates the process of updating NISAR (NIAID Information Systems Architecture Repository) with data from Jira issues. It fetches CAB (Change Advisory Board) requests from a Jira filter, parses the structured CAB description fields, and fills out the NISAR web form using browser automation.

NISAR requires access from the NIAID network or VPN.

## Features

- **Jira Integration**: Fetches issues from a specified Jira filter using REST API and PAT authentication.
- **CAB Data Parsing**: Extracts structured fields from Jira issue descriptions (e.g., Describe the Change, Business Owner, Deployment Date).
- **Conditional Logic**: Selects NISAR form options based on Jira issue status (e.g., System vs. Post-Implementation radio buttons).
- **Browser Automation**: Uses Selenium to navigate NISAR, fill forms, and handle interactions like lookups and selections.
- **Error Handling**: Detects server errors, handles alerts, and provides feedback on automation steps.
- **Configurable**: All URLs, credentials, and mappings are stored in `config.json`.

## Prerequisites

- Python 3.7+
- Access to NIAID VPN or network for NISAR access
- Microsoft Edge browser (WebDriver included)
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

The script processes the first issue from the filter, parses CAB data, and automates the NISAR form. Check the console output for progress and any errors.

## Configuration

Edit `config.json` to customize:

- `jira_url`: Jira base URL
- `jira_pat`: Your Personal Access Token
- `jira_filter_url`: URL of the Jira filter to fetch issues
- `nisar_web_url`: NISAR management page URL
- `nisar_form_url`: NISAR form URL
- `presenter_branch`: Branch for CAB presenter lookup
- `cab_field`: Jira custom field ID for CAB description

## How It Works

1. **Fetch Jira Data**: Queries the Jira API for issues matching the filter.
2. **Parse CAB Fields**: Extracts key-value pairs from the CAB description using predefined keywords.
3. **Determine Form Type**: Based on issue status, selects the appropriate NISAR form section (System or Post-Implementation).
4. **Automate NISAR**:
   - Navigates to NISAR and opens the form.
   - Fills fields in order: Summary, radio buttons, system search/selection, CAB details.
   - Handles lookups, alerts, and validations.
5. **Submit**: Attempts to submit the form.

## Project Structure

- `main.py`: Main script for Jira fetching and NISAR automation.
- `config.json`: Configuration file (ignored by Git for security).
- `requirements.txt`: Python dependencies.
- `msedgedriver.exe`: Microsoft Edge WebDriver binary.
- `.gitignore`: Excludes sensitive files from version control.
- `README.md`: This file.

## Contributing

Submit issues or pull requests for improvements.

## License

This project is licensed under the MIT License.
