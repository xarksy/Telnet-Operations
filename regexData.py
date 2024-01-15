import re

# This function extracts specific details about an ONU
def onu_detail(data):
    nameCust = re.search(r'Name:\s*([^\s].*)', data)
    serialCust = re.search(r'Serial number:\s*([^\s].*)', data)
    statusCust = re.search(
        r'Config state:\s*([^\s]+)', data)
    phaseCust = re.search(
        r'Phase state:\s*([^\s]+)', data)
    onudistCust = re.search(
        r'ONU Distance:\s*([^\s]+)', data)
    onlinedurCust = re.search(
        r'Online Duration:\s*([^\s].*)', data)

    return nameCust[1], serialCust[1], statusCust[1], phaseCust[1], onudistCust[1], onlinedurCust[1]

# This function extracts Wide Area Network (WAN) details of an ONU
def onu_wan(data1):
    try:
        username = re.search(r'Username:\s*([^\s]+)', data1)
        # username = re.search(r'\d+@prisma.net', data1)
        status = re.search(r'Status:\s*([^\s]+)', data1)
    except:
        username = 'not set'
        status = 'N/A'
    try:
        cvlan = re.search(r'CVLAN:\s*([^\s]+)', data1)
        cvlan = cvlan[1]
        currip = re.search(r'Current IP:\s*([^\s]+)', data1)
        currip = currip[1]
        macAddres = re.search(r'MAC address:\s*([^\s]+)', data1)
        macAddres = macAddres[1]
    except:
        cvlan = 'N/A'
        currip = 'N/A'
        macAddres = 'N/A'

    return username[1], status[1], cvlan, currip, macAddres

# This function extracts information related to redaman for a specific ONU
def onu_redaman(onuidnya, data2):
    redamanCust = re.search(rf'{onuidnya}\s*([^\s].*)', data2)
    return redamanCust[1]

# This function extracts equipment details of an ONU
def onu_equip(data3):
    vendorID = re.search(r'Vendor ID:\s*([^\s]+)', data3)
    version = re.search(r'Version:\s*([^\s]+)', data3)
    equipmentID = re.search(r'Equipment ID:\s*([^\s]+.*)', data3)

    return vendorID[1], version[1], equipmentID[1]
