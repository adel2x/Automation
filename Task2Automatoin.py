import requests
import urllib3
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Replace with your bot token and chat ID
bot_token = "8154599120:AAHum7_ru_osMX4082iOv2bNk1T2KI-5R-s"
chat_id = "813385620"

def get_index_size(elasticUrl, indexName):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic ZWxhc3RpYzpHKm1rXzlrLXVQSlNUWnNTTzZIWg=="
    }
    
    # Corrected the string formatting for the URL
    url = f"{elasticUrl}/{indexName}/_disk_usage?run_expensive_tasks=true&pretty"
    
    # Perform the POST request and set verify=False to ignore SSL certificate errors
    response = requests.post(url, verify=False, headers=headers)
    
    if response.status_code == 200:
        # Parse the response JSON to access the index details
        response_data = response.json()  # Extract JSON from response

        # Get the current timestamp
        current_timestamp = datetime.now()
        
        # Extract the store size in bytes and convert to MB
        size_in_mb = response_data[indexName]["store_size_in_bytes"] / (1024 * 1024)
        
        # Return the index information
        return {
            "index": indexName,
            "size_in_mb": size_in_mb,
            "timestamp": current_timestamp
        }
    else:
        print(f"Failed to retrieve index size for {indexName}, Status Code: {response.status_code}")
        return None

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"  # Use HTML for formatting
    }

    response = requests.post(url, json=payload,verify=True)

    if response.status_code == 200:
        print("Report message sent successfully!")
    else:
        print("Failed to send Telegram message, Status Code:", response.status_code)

def delete_index_logs(elasticUrl, indexName):
    url = f"{elasticUrl}/{indexName}/_delete_by_query"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic ZWxhc3RpYzpHKm1rXzlrLXVQSlNUWnNTTzZIWg=="
    }

    payload = {
        "query": {
            "range": {
                "@timestamp": {
                    "lt": "now-2h"
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload,verify=False)

    if response.status_code == 200:
        print("Retention policy applied successfully!")
    else:
        print("Failed to apply retention policy, Status Code:", response.status_code)

def main():
    indexName = input("Enter index name: ")
    elasticUrl = input("Enter Elasticsearch URL: ")
    
    # Fetch index size details
    allFields = get_index_size(elasticUrl, indexName)
    
    if allFields:
        if allFields['size_in_mb'] > 2:
            # Send a message to Telegram if the index size exceeds 2 MB
            message = f"Index {indexName} has exceeded the size limit with {allFields['size_in_mb']} MB."
            send_telegram_message(bot_token, chat_id, message)
            
            # Apply retention policy
            delete_index_logs(elasticUrl, indexName)
            
            print("Exiting...")
        else:
            print(f"Index size is {allFields['size_in_mb']} MB, below the threshold.")
    else:
        print("Failed to check index size!")

if __name__ == '__main__':
    main()
