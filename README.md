# Script-Instagram-User-Bot

## Purpose of the Script
The purpose of this script is very simple: it is used to identify spammer accounts among the followers of an Instagram profile. It uses the Selenium library to automate the process of logging in, navigating, and analyzing follower profiles.

## Instructions
1. Ensure you have ChromeDriver and Selenium installed.
2. Enter your Instagram credentials in the `username` and `password` fields at the beginning of the script. You can use environment variables for better security.
3. Run the script using a code editor like Visual Studio Code or any other editor of your choice.

## Attention
- **Credential Security:** Ensure you do not share your Instagram credentials with anyone. Use environment variables to protect your personal information.
- **Intended Use:** This script is intended solely for identifying spammer accounts and should not be used for other purposes.

## Running the Script
```python
# Ensure you have properly configured your credentials
username = os.environ.get('INSTAGRAM_USERNAME', 'your_username')
password = os.environ.get('INSTAGRAM_PASSWORD', 'your_password')

# Run the script from your preferred code editor
