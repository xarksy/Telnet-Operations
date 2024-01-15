from fungsi import *
import concurrent.futures

# List of dictionaries representing different areas with their connection details
areas = [
    {
        'host': '103.148.2.110',
        'port': '333',
        'username': 'usernameArea234',
        'password': 'passwordArea234'
    },
    {
        'host': '103.148.2.58',
        'port': '1111',
        'username': 'usernameArea1',
        'password': 'passwordArea1'
    },
    {
        'host': '103.148.2.170',
        'port': '2222',
        'username': 'usernameArea234',
        'password': 'passwordArea234'
    },
    {
        'host': '103.148.2.170',
        'port': '44444',
        'username': 'usernameArea234',
        'password': 'passwordArea234'
    }
]

awal = time.perf_counter() # Record the start time

# Using ThreadPoolExecutor to concurrently execute telnetin function for each area
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = []

    # Telnetin function execution for each area
    for area in areas:
        future = executor.submit(
            telnetin, area['host'], area['port'], area['username'], area['password']
        )
        futures.append(future)

    # Handling results of telnetin function
    for future in futures:
        try:
            return_value = future.result()
            area['filename_hasilssh'] = return_value[2]
            area['ipnya'] = return_value[3]
            area['portnya'] = return_value[4]
            print(return_value[2])
            # Perform other operations with return_value as needed
        except Exception as e:
            print(f"Telnet operation failed: {e}")
    
    # ========================= 1st process
    futures = []
    # telnetin_customer_detail function execution for each area
    for area in areas:
        future = executor.submit(
            telnetin_customer_detail, area['host'], area['port'], area['username'], area['password'],area['filename_hasilssh']
        )
        futures.append(future)

    # Handling results of telnetin function
    for future in futures:
        try:
            return_value = future.result()
            # Perform other operations with return_value as needed
        except Exception as e:
            print(f"Telnet operation failed: {e}")
    
    # ========================= 2nd process
    futures = []
    # telnetin_customer_onu function execution for each area
    for area in areas:
        future = executor.submit(
            telnetin_customer_onu, area['host'], area['port'], area['username'], area['password'],area['filename_hasilssh']
        )
        futures.append(future)

    # Handling results of telnetin function
    for future in futures:
        try:
            return_value = future.result()
            # Perform other operations with return_value as needed
        except Exception as e:
            print(f"Telnet operation failed: {e}")
    

    # ========================= 3rd process
    futures = []
    # telnetin_customer_wan function execution for each area
    for area in areas:
        future = executor.submit(
            telnetin_customer_wan, area['host'], area['port'], area['username'], area['password'],area['filename_hasilssh']
        )
        futures.append(future)

    # Handling results of telnetin function
    for future in futures:
        try:
            return_value = future.result()
            # Perform other operations with return_value as needed
        except Exception as e:
            print(f"Telnet operation failed: {e}")
    
    # ========================= 4th process
    futures = []
    # telnetin_customer_pppoe function execution for each area
    for area in areas:
        future = executor.submit(
            telnetin_customer_pppoe, area['host'], area['port'], area['username'], area['password'],area['filename_hasilssh']
        )
        futures.append(future)

    # Handling results of telnetin function
    for future in futures:
        try:
            return_value = future.result()
            # Perform other operations with return_value as needed
        except Exception as e:
            print(f"Telnet operation failed: {e}")
    
    # ========================= 5th process
    futures = []
    # telnetin_customer_wan_redaman function execution for each area
    for area in areas:
        future = executor.submit(
            telnetin_customer_wan_redaman, area['host'], area['port'], area['username'], area['password'],area['filename_hasilssh']
        )
        futures.append(future)

    # Handling results of telnetin function
    for future in futures:
        try:
            return_value = future.result()
            # Perform other operations with return_value as needed
        except Exception as e:
            print(f"Telnet operation failed: {e}")
    
# Performing autoupdatedb.updating_file for each area
for area in areas:
    future = autoupdatedb.updating_file(
        area['filename_hasilssh'],area['ipnya'],area['portnya']
    )

akhir = time.perf_counter() # Record the end time
print(akhir-awal)
