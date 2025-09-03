from netmiko import ConnectHandler
import pwinput
import re
import pandas as pd

# Keywords to identify access points
access_point_keywords = ['air', 'air-ap', 'air-lap', 'air-sap', 'access point', 'access-point', 'c91']

# Step 0: Ask for log and Excel filenames
log_filename = input("Enter the log file name (e.g., log.txt): ")
excel_filename = input("Enter the Excel file name to export (without .xlsx): ")

# Open log file
logfile = open(log_filename, "w", encoding="utf-8")

# Step 1: Get credentials and IP list
username = input("Username: ")
password = pwinput.pwinput(prompt="Password: ", mask="*")
ip_input = input("Enter switch IPs (comma-separated): ")
ip_list = [ip.strip() for ip in ip_input.split(",")]

# Collect AP info here
ap_data = []

# Step 2: Loop through switches
for device_ip in ip_list:
    print(f"\n-------------- 🔌 Connecting to {device_ip}... --------------")
    print(f"\n-------------- 🔌 Connecting to {device_ip}... --------------", file=logfile)

    device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }

    try:
        net_connect = ConnectHandler(**device)
        hostname = net_connect.find_prompt().rstrip('#>')
        print(f"✅ Connected to {hostname}")
        print(f"✅ Connected to {hostname}", file=logfile)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"❌ Connection failed: {e}", file=logfile)
        continue

    # Step 3: Run CDP neighbors detail
    print("🔍 Fetching CDP neighbor details...")
    print("🔍 Fetching CDP neighbor details...", file=logfile)
    cdp_output = net_connect.send_command("show cdp neighbors detail")

    # Step 4: Parse and show only APs
    blocks = cdp_output.split("Device ID:")
    ap_found = False

    for block in blocks[1:]:  # skip the first split which is empty
        lines = block.strip().splitlines()
        device_id = lines[0].strip()

        platform_line = next((line for line in lines if "Platform:" in line), "")
        interface_line = next((line for line in lines if "Interface:" in line and "Port ID" in line), "")

        # Extract and normalize platform
        platform = platform_line.split(",")[0].replace("Platform: ", "").strip().lower()
        platform = platform.replace("cisco", "").replace(" ", "")

        # Check if it's an access point
        if any(keyword in platform for keyword in access_point_keywords):
            ap_found = True
            match = re.search(r"Interface:\s+(\S+)", interface_line)
            local_interface = match.group(1) if match else "Unknown"

            ap_data.append({
                "Device IP": device_ip,
                "Hostname": hostname,
                "Device ID": device_id,
                "Local Interface": local_interface,
                "Platform": platform
            })

            print("\n----------------")
            print(f"📡 Access Point Detected")
            print(f"Local Interface: {local_interface}")
            print(f"Platform       : {platform}")
            print("------------------")

            print("\n----------------", file=logfile)
            print(f"📡 Access Point Detected", file=logfile)
            print(f"Local Interface: {local_interface}", file=logfile)
            print(f"Platform       : {platform}", file=logfile)
            print("------------------", file=logfile)

    if not ap_found:
        print("🚫 No Access Points found via CDP.")
        print("🚫 No Access Points found via CDP.", file=logfile)

    net_connect.disconnect()
    print(f"--------------🔌 Disconnected from {device_ip}--------------")
    print(f"--------------🔌 Disconnected from {device_ip}--------------", file=logfile)

# Step 5: Export to Excel
if ap_data:
    df = pd.DataFrame(ap_data)
    excel_output = f"{excel_filename}.xlsx"
    df.to_excel(excel_output, index=False)
    print(f"\n📄 Excel file saved as: {excel_output}")
    print(f"\n📄 Excel file saved as: {excel_output}", file=logfile)
else:
    print("\n⚠ No access point data to export.")
    print("\n⚠ No access point data to export.", file=logfile)

logfile.close()
input("\n✅ Press Enter to exit...")


excel file integration
