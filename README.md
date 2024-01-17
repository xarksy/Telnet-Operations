# Telnet Operations with ThreadPoolExecutor
This script performs telnet operations on multiple areas concurrently using the ThreadPoolExecutor from the **'concurrent.futures'** module. The telnet operations include retrieving information and updating files for different areas.

### Prerequisites
Python 3.x
Dependencies listed in the requirements.txt file

### Configuration
areas: A list of dictionaries, each containing the connection details (host, port, username, password) for a specific area.

### Functionality
1. Telnet Operations (ThreadPoolExecutor):
The script uses ThreadPoolExecutor to concurrently execute the telnetin function for each area.
The result of each telnetin operation is used to update information in the areas list.
2. Telnet Operations for Specific Tasks:
Subsequent telnet operations (telnetin_customer_detail, telnetin_customer_onu, etc.) are performed using ThreadPoolExecutor for specific tasks related to each area.
3. Additional Functions:
The fungsi folder contains additional functions in the additional_functions.py file.
4. Updating Files:
The script calls autoupdatedb.updating_file for each area, providing the necessary information obtained from the telnet operations.
5. Execution Time:
The total execution time of the script is calculated and printed at the end.

### Error Handling
The script handles exceptions during telnet operations and prints an error message if any operation fails.

### Notes
Ensure that the necessary functions (telnetin, telnetin_customer_detail, etc.) are defined in the telnet_functions.py file.
Customize the areas list with the specific connection details for the areas you want to operate on.

### Author
Sandra
