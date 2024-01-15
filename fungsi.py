import time
import re
from telnetlib import Telnet
import autoupdatedb
from regexData import *
from cekSQlite import *


awal = time.perf_counter()

# Global variable
total = []
list_slotportonuid = []
passed_listslotportonuid = []

# Function to handle telnet connection and update customer ONU states
def telnetin(host, port, username, password):
    # Creating db to be saved later
    hasil_onu_state = autoupdatedb.saving_file(host, port)
    
    # Establishing connection and logging in
    conn = Telnet(host, port)
    conn.write(username.encode('ascii') + b"\n")
    conn.write(password.encode('ascii') + b"\n")

    # Gathering customer's onu state
    conn.write(b'show gpon onu state\n')
    hostnamenya = conn.read_until(b"#").decode('ascii')
    print(hostnamenya)

    # Deciding how many times reading the network stream
    if 'NNN01-D1-SPP-09#' in hostnamenya:
        jumlahLoop = 4
        print(jumlahLoop)
        currentStream = conn.read_until(b"--More--").decode('ascii')
        data_onu_state(currentStream, hasil_onu_state, host)
        print(currentStream)
    else:
        jumlahLoop = 60
        print(jumlahLoop)
        currentStream = conn.read_until(b"--More--").decode('ascii')
        print(currentStream)
        data_onu_state(currentStream, hasil_onu_state, host)

    # Starting gather the data
    for _ in range(jumlahLoop):
        conn.write(b' ')
        currentStream = conn.read_until(b"ONU Number:", 1).decode('ascii')
        if 'ONU Number:' not in currentStream:
            data_onu_state(currentStream, hasil_onu_state, host)
        else:
            data_onu_state(currentStream, hasil_onu_state, host)
            break
    
    
    akhir = time.perf_counter()
    print(akhir-awal)
    closingConnection(conn)
    
    # Closing the database
    hasil_onu_state[1].close()

    # Returning database
    return hasil_onu_state

# Function to update customer onu statuses into database
def data_onu_state(datanya, hasil_onu_state, host):

    # Gathering slot port onuid from datanya
    all_list_onu = re.findall('\d/\d+/\d+:\d+.*', datanya)

    # Looping each found data to extract it
    for datayangDicari in all_list_onu:
        data_mentah = re.split(r'\s+', datayangDicari)
        slotportonuid = data_mentah[0]
        list_slotportonuid.append(slotportonuid)
        total.append(slotportonuid)
        hasil = slotportonuid.split('/')
        ambil_port_onuid = hasil[2].split(':')

        shelf = hasil[0]
        slot = hasil[1]
        port = ambil_port_onuid[0]
        onu_id = ambil_port_onuid[1]
        Admin_State = data_mentah[1]
        OMCC_State = data_mentah[2]
        Phase_State = data_mentah[3]
        Channel = data_mentah[4]

        # Updating into database
        hasil_onu_state[0].execute('''INSERT OR IGNORE INTO dapel(slotportonuid,shelf,slot,port,onuid,adminstate,omccstate,phasestate,channel) values(?,?,?,?,?,?,?,?,?)''',
                                   (slotportonuid, shelf, slot, port, onu_id, Admin_State, OMCC_State, Phase_State, Channel))
        hasil_onu_state[1].commit()
        print(host, shelf, slot, port, onu_id,
              slotportonuid, Admin_State, OMCC_State, Phase_State, Channel)

# Function to handle telnet connection, gather detail of customer's ont and update the database
def telnetin_customer_detail(host, port, username, password, nama_dbnya):
    # Establishing connection
    session = establishingSession(host,port,username,password,nama_dbnya)
    conn = session[0]

    # Checking which online customer
    list_slotportonuid = cobaceksqlite(session[1])
    jumlahProses = 0  # counter

    # Looping through all online customer
    for slotPortOnuIdCust in list_slotportonuid:
        print(host, slotPortOnuIdCust)

        # Noting it into slotport lists
        passed_listslotportonuid.append(slotPortOnuIdCust)
        jumlahProses = jumlahProses + 1
        remaining = len(list_slotportonuid) - jumlahProses
        print(remaining, 'data lagi')
        print('passed count : ', len(passed_listslotportonuid))
        
        # Gathering customer's onu detail info
        templateSyntax = 'show gpon onu detail-info gpon-onu_'+slotPortOnuIdCust
        conn.write(templateSyntax.encode('ascii') + b"\n")
        data_detail_info = conn.read_until(b"--More--").decode('ascii')
        hasil_detail = onu_detail(data_detail_info)
        print(hasil_detail)
        conn.write(b' ')
        conn.write(b'\n')

        # Updating into database
        session[1].execute('''UPDATE dapel SET name = ?, sn = ?, statuscust = ?, phasestate = ?, onudistance = ?, onlineduration = ? WHERE slotportonuid = ?''',
                              (hasil_detail[0], hasil_detail[1], hasil_detail[2], hasil_detail[3], hasil_detail[4], hasil_detail[5], slotPortOnuIdCust))
        session[2].commit()

    closingConnection(conn)
    akhir = time.perf_counter()
    print(akhir-awal)

    # Closing the database
    session[2].close()

# Function to handle telnet connection, gather onu configuration of customer's ont and update the database
def telnetin_customer_onu(host, port, username, password, nama_dbnya):
    # Establishing connection
    session = establishingSession(host,port,username,password,nama_dbnya)
    conn = session[0]


    list_slotportonuid = cobaceksqlite(session[1])
    jumlahProses = 0  # counter
    
    # Looping through all online customer
    for slotPortOnuIdCust in list_slotportonuid:
        data_wan = ''
        print(host, slotPortOnuIdCust)
        passed_listslotportonuid.append(slotPortOnuIdCust)
        jumlahProses = jumlahProses + 1
        remaining = len(list_slotportonuid) - jumlahProses
        print(remaining, 'data lagi')
        print('passed count : ', len(passed_listslotportonuid))

        # Gathering customer's onu configuration
        templateSyntax = 'show onu running config gpon-onu_'+slotPortOnuIdCust
        conn.write(templateSyntax.encode('ascii') + b"\n")
        data_wan = conn.read_until(b"!", timeout=3).decode('ascii')

        # Categorizing customer's connection type and updating database
        if ('pppoe 1 nat enable user') in data_wan:
            print('------------------ pppoe')
            session[1].execute(
                '''UPDATE dapel SET connection = ? WHERE slotportonuid = ?''', ('pppoe', slotPortOnuIdCust))
            session[2].commit()
        elif ('wan-ip 1 mode pppoe') in data_wan:
            print('------------------ wan-ip')
            session[1].execute(
                '''UPDATE dapel SET connection = ? WHERE slotportonuid = ?''', ('wan-ip', slotPortOnuIdCust))
            session[2].commit()
        else:
            print('------------------ notset')
            session[1].execute(
                '''UPDATE dapel SET connection = ? WHERE slotportonuid = ?''', ('notset', slotPortOnuIdCust))
            session[2].commit()

        conn.write(b' ')
        conn.write(b'\n')


    closingConnection(conn)
    akhir = time.perf_counter()
    print(akhir-awal)

    # Closing the database
    session[2].close()

# Function to handle telnet connection, gather wan of customer's ont and update the database
def telnetin_customer_wan(host, port, username, password, nama_dbnya):
    # Establishing connection
    session = establishingSession(host,port,username,password,nama_dbnya)
    conn = session[0]

    # Checking which customer ont's has wan ip configuration
    list_slotportonuid = cobaceksqliteconnectionwanip(session[1])
    jumlahProses = 0  # counter

    # Looping through all customer ont's has wan ip configuration
    for slotPortOnuIdCust in list_slotportonuid:
        print(host, slotPortOnuIdCust)
        passed_listslotportonuid.append(slotPortOnuIdCust)
        jumlahProses = jumlahProses + 1
        remaining = len(list_slotportonuid) - jumlahProses
        print(remaining, 'data lagi')
        print('passed count : ', len(passed_listslotportonuid))

        # Gathering customer's onu wan info
        templateSyntax = 'show gpon remote-onu wan-ip gpon-onu_'+slotPortOnuIdCust
        conn.write(templateSyntax.encode('ascii') + b"\n")
        data_wan = conn.read_until(
            b"IP host ID:", timeout=30).decode('ascii')
        if ('No relate information to show.') in data_wan:
            hasil_wan = onu_wan('notset')


        hasil_wan = onu_wan(data_wan)
        conn.write(b' ')
        conn.write(b'\n')

        print(hasil_wan[0], hasil_wan[1],
              hasil_wan[2], hasil_wan[3], hasil_wan[4])
        
        # Updating database
        session[1].execute('''UPDATE dapel SET username = ?, statuswan = ?, cvlan = ?, currentip = ?, macaddress = ? WHERE slotportonuid = ?''',
                              (hasil_wan[0], hasil_wan[1], hasil_wan[2], hasil_wan[3], hasil_wan[4], slotPortOnuIdCust))
        session[2].commit()

    closingConnection(conn)
    akhir = time.perf_counter()
    print(akhir-awal)
    
    # Closing database 
    session[2].close()

# Function to handle telnet connection, gather pppoe of customer's ont and update the database
def telnetin_customer_pppoe(host, port, username, password, nama_dbnya):
    # Establishing connection
    session = establishingSession(host,port,username,password,nama_dbnya)
    conn = session[0]

    # Checking which customer ont's has pppoe configuration
    list_slotportonuid = cobaceksqliteconnectionpppoe(session[1])
    jumlahProses = 0  # counter

    # Looping through all customer ont's has pppoe configuration
    for slotPortOnuIdCust in list_slotportonuid:
        print(host, slotPortOnuIdCust)
        passed_listslotportonuid.append(slotPortOnuIdCust)
        jumlahProses = jumlahProses + 1
        remaining = len(list_slotportonuid) - jumlahProses
        print(remaining, 'data lagi')
        print('passed count : ', len(passed_listslotportonuid))

        # Gathering customer's onu pppoe
        templateSyntax = 'show gpon remote-onu pppoe gpon-onu_'+slotPortOnuIdCust
        conn.write(templateSyntax.encode('ascii') + b"\n")
        data_wan = conn.read_until(b"IP host ID:", timeout=1).decode('ascii')
        if ('No relate information to show.') in data_wan:
            hasil_wan = onu_wan('notset')

        hasil_wan = onu_wan(data_wan)
        # print(hasil_wan)
        conn.write(b' ')
        conn.write(b'\n')

        print('pppoe : ', hasil_wan[0], hasil_wan[1],
              hasil_wan[2], hasil_wan[3], hasil_wan[4])

        # Updating database
        session[1].execute('''UPDATE dapel SET username = ?, statuswan = ?, cvlan = ?, currentip = ?, macaddress = ? WHERE slotportonuid = ?''',
                              (hasil_wan[0], hasil_wan[1], hasil_wan[2], hasil_wan[3], hasil_wan[4], slotPortOnuIdCust))
        session[2].commit()

    closingConnection(conn)
    akhir = time.perf_counter()
    print(akhir-awal)

    # Closing database
    session[2].close()

# Function to handle telnet connection, gather redaman of customer's ont and update the database
def telnetin_customer_wan_redaman(host, port, username, password, nama_dbnya):
    # Establishing connection
    session = establishingSession(host,port,username,password,nama_dbnya)
    conn = session[0]

    # Checking which online ont
    list_slotportonuid = cobaceksqliteredaman(session[1])
    jumlahProses = 0  # counter
    for slotPortOnuIdCust in list_slotportonuid:
        print(host, slotPortOnuIdCust)
        passed_listslotportonuid.append(slotPortOnuIdCust)
        jumlahProses = jumlahProses + 1
        remaining = len(list_slotportonuid) - jumlahProses
        print(remaining, 'data lagi')
        print('passed count : ', len(passed_listslotportonuid))

        # Gathering customer's onu redaman
        templateSyntax = 'show pon power olt-rx gpon-onu_'+slotPortOnuIdCust
        conn.write(templateSyntax.encode('ascii') + b"\n")
        data_redaman = conn.read_until(b"(dbm)", timeout=1).decode('ascii')

        hasil_redaman = onu_redaman(slotPortOnuIdCust, data_redaman)
        print(hasil_redaman)
        conn.write(b' ')
        conn.write(b'\n')

        # Updating database
        session[1].execute('''UPDATE dapel SET redamancust = ? WHERE slotportonuid = ?''',
                              (hasil_redaman, slotPortOnuIdCust))
        session[2].commit()

    closingConnection(conn)
    akhir = time.perf_counter()
    print(akhir-awal)

    # Closing database
    session[2].close()

# Establishing connection, loggin in and opening database
def establishingSession(host,port,username,password,nama_dbnya):
    # Opening existing database
    updateCust = autoupdatedb.updating_customer_file(nama_dbnya)
    cur = updateCust[0]
    con = updateCust[1]

    # Establishing connection and logging in
    conn = Telnet(host, port)
    conn.write(username.encode('ascii') + b"\n")
    conn.write(password.encode('ascii') + b"\n")
    conn.write(b'configure terminal\n')

    return conn,cur,con

# Closing connection
def closingConnection(conn):
    conn.write(b'exit\n')
    conn.write(b'exit\n')
    conn.write(b'yes\n')
