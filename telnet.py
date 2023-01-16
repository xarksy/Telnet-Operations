
from contextlib import nullcontext
from operator import eq
import time
import re
from datetime import datetime
from telnetlib import Telnet
import sqlite3
import os.path
import autoupdatedb
import concurrent.futures


current_dir = os.getcwd()

if not os.path.isdir("rekapan"):
    os.makedirs("rekapan")

if not os.path.isdir("hasil"):
    os.makedirs("hasil")


def saving_file(ipnya):
    ipnya = re.sub(".", "-", ipnya)
    filename_hasilssh = r'rekapan/' + ipnya + ' ' + \
        datetime.today().strftime('%d-%m-%Y %I-%M %p') + '.db'
    con = sqlite3.connect(filename_hasilssh)
    cur = con.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS dapel(
            slotportonuid text, shelf text, slot text, port text, onuid text,
            adminstate text, omccstate text, phasestate text, channel text,
            name text, sn text, statuscust text, cvlan text, onudistance text, onlineduration text,
            username text, statuswan text, currentip text, macaddress text,
            redamancust text,
            vendorid text, version text, equipmentid text)  ''')

    return con, cur


total = []
list_slotportonuid = []
passed_listslotportonuid = []


def telnetin(host, port, username, password):
    # ====================
    hasil_onu_state = autoupdatedb.saving_file(host)
    # ====================

    conn = Telnet(host, port)
    conn.write(username.encode('ascii') + b"\n")
    conn.write(password.encode('ascii') + b"\n")
    conn.write(b'show gpon onu state\n')
    wew = conn.read_until(b"--More--").decode('ascii')
    data_onu_state(wew, hasil_onu_state, host)
    for _ in range(60):
        conn.write(b' ')
        wew = conn.read_until(b"ONU Number:", 1).decode('ascii')
        if 'ONU Number:' not in wew:
            data_onu_state(wew, hasil_onu_state, host)
        else:
            data_onu_state(wew, hasil_onu_state, host)
            break
    # tutup DB
    hasil_onu_state[1].close()

    return hasil_onu_state


def data_onu_state(datanya, hasil_onu_state, host):

    all_list_onu = re.findall('\d/\d+/\d+:\d+.*', datanya)
    for ketemu in all_list_onu:
        data_mentah = re.split(r'\s+', ketemu)
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

        hasil_onu_state[0].execute('''INSERT OR IGNORE INTO dapel(slotportonuid,shelf,slot,port,onuid,adminstate,omccstate,phasestate,channel) values(?,?,?,?,?,?,?,?,?)''',
                                   (slotportonuid, shelf, slot, port, onu_id, Admin_State, OMCC_State, Phase_State, Channel))
        hasil_onu_state[1].commit()
        print(host, shelf, slot, port, onu_id,
              slotportonuid, Admin_State, OMCC_State, Phase_State, Channel)


def telnetin_customer_detail(host, port, username, password, nama_dbnya):
    # =========================
    updateCust = autoupdatedb.updating_customer_file(nama_dbnya)
    # =========================

    conn = Telnet(host, port)
    conn.write(username.encode('ascii') + b"\n")
    conn.write(password.encode('ascii') + b"\n")
    listcummy = ['1/1/1:7']
    conn.write(b'configure terminal\n')
    time.sleep(2)
    list_slotportonuid = cobaceksqlite(updateCust[0])
    i = 0  # counter
    for yes in list_slotportonuid:
        print(host, yes)
        passed_listslotportonuid.append(yes)
        i = i + 1
        remaining = len(list_slotportonuid) - i
        print(remaining, 'data lagi')
        print('passed count : ', len(passed_listslotportonuid))
        # =========================== 1
        wesya = 'show gpon onu detail-info gpon-onu_'+yes
        conn.write(wesya.encode('ascii') + b"\n")
        data_detail_info = conn.read_until(b"--More--").decode('ascii')
        hasil_detail = onu_detail(data_detail_info)
        print(hasil_detail)
        conn.write(b' ')
        conn.write(b'\n')

        updateCust[0].execute('''UPDATE dapel SET name = ?, sn = ?, statuscust = ?, phasestate = ?, onudistance = ?, onlineduration = ? WHERE slotportonuid = ?''',
                              (hasil_detail[0], hasil_detail[1], hasil_detail[2], hasil_detail[3], hasil_detail[4], hasil_detail[5], yes))
        updateCust[1].commit()

    conn.write(b'exit\n')
    conn.write(b'exit\n')
    conn.write(b'yes\n')
    akhir = time.perf_counter()
    print(akhir-awal)
    # tutup DB
    updateCust[1].close()


def telnetin_customer_wan1(host, port, username, password, nama_dbnya):
    # =========================
    updateCust = autoupdatedb.updating_customer_file(nama_dbnya)
    # =========================
    conn = Telnet(host, port)
    conn.write(username.encode('ascii') + b"\n")
    conn.write(password.encode('ascii') + b"\n")
    listcummy = ['1/1/1:7']
    conn.write(b'configure terminal\n')
    time.sleep(2)
    list_slotportonuid = cobaceksqliteconnectionwanip(updateCust[0])
    i = 0  # counter
    for yes in list_slotportonuid:
        print(host, yes)
        passed_listslotportonuid.append(yes)
        i = i + 1
        remaining = len(list_slotportonuid) - i
        print(remaining, 'data lagi')
        print('passed count : ', len(passed_listslotportonuid))

        # =========================== 2
        wesya = 'show gpon remote-onu wan-ip gpon-onu_'+yes
        conn.write(wesya.encode('ascii') + b"\n")
        data_wan = conn.read_until(
            b"IP host ID:", timeout=1).decode('ascii')
        if ('IP host ID:') not in data_wan:
            time.sleep(1)
            print('masuk sini 2')
            wesya = 'show gpon remote-onu pppoe gpon-onu_'+yes
            conn.write(wesya.encode('ascii') + b"\n")
            # /r/n?
            data_wan = conn.read_until(
                b"\r\n", timeout=1).decode('ascii')
            hasil_wan = onu_wan(data_wan)
            print(data_wan)
            if ('No relate information to show.') in data_wan:
                hasil_wan = onu_wan('notset')

        hasil_wan = onu_wan(data_wan)
        # print(hasil_wan)
        conn.write(b' ')
        conn.write(b'\n')

        print(hasil_wan[0], hasil_wan[1],
              hasil_wan[2], hasil_wan[3], hasil_wan[4])
        updateCust[0].execute('''UPDATE dapel SET username = ?, statuswan = ?, cvlan = ?, currentip = ?, macaddress = ? WHERE slotportonuid = ?''',
                              (hasil_wan[0], hasil_wan[1], hasil_wan[2], hasil_wan[3], hasil_wan[4], yes))
        updateCust[1].commit()

    conn.write(b'exit\n')
    conn.write(b'exit\n')
    conn.write(b'yes\n')
    akhir = time.perf_counter()
    print(akhir-awal)
    # tutup DB
    updateCust[1].close()


def telnetin_customer_onu(host, port, username, password, nama_dbnya):
    # =========================
    updateCust = autoupdatedb.updating_customer_file(nama_dbnya)
    # =========================

    conn = Telnet(host, port)
    conn.write(username.encode('ascii') + b"\n")
    conn.write(password.encode('ascii') + b"\n")
    listcummy = ['1/1/1:7']
    conn.write(b'configure terminal\n')
    time.sleep(2)
    list_slotportonuid = cobaceksqlite(updateCust[0])
    i = 0  # counter
    for yes in list_slotportonuid:
        data_wan = ''
        print(host, yes)
        passed_listslotportonuid.append(yes)
        i = i + 1
        remaining = len(list_slotportonuid) - i
        print(remaining, 'data lagi')
        print('passed count : ', len(passed_listslotportonuid))
        # =========================== 2
        wesya = 'show onu running config gpon-onu_'+yes
        conn.write(wesya.encode('ascii') + b"\n")
        data_wan = conn.read_until(b"!", timeout=3).decode('ascii')

        if ('pppoe 1 nat enable user') in data_wan:
            print('------------------ pppoe')
            updateCust[0].execute(
                '''UPDATE dapel SET connection = ? WHERE slotportonuid = ?''', ('pppoe', yes))
            updateCust[1].commit()
        elif ('wan-ip 1 mode pppoe') in data_wan:
            print('------------------ wan-ip')
            updateCust[0].execute(
                '''UPDATE dapel SET connection = ? WHERE slotportonuid = ?''', ('wan-ip', yes))
            updateCust[1].commit()
        else:
            print('------------------ notset')
            updateCust[0].execute(
                '''UPDATE dapel SET connection = ? WHERE slotportonuid = ?''', ('notset', yes))
            updateCust[1].commit()

        conn.write(b' ')
        conn.write(b'\n')

    conn.write(b'exit\n')
    conn.write(b'exit\n')
    conn.write(b'yes\n')
    akhir = time.perf_counter()
    print(akhir-awal)
    # tutup DB
    updateCust[1].close()


def telnetin_customer_wan(host, port, username, password, nama_dbnya):
    # =========================
    updateCust = autoupdatedb.updating_customer_file(nama_dbnya)
    # =========================

    conn = Telnet(host, port)
    conn.write(username.encode('ascii') + b"\n")
    conn.write(password.encode('ascii') + b"\n")
    listcummy = ['1/1/1:7']
    conn.write(b'configure terminal\n')
    time.sleep(2)
    list_slotportonuid = cobaceksqliteconnectionwanip(updateCust[0])
    i = 0  # counter
    for yes in list_slotportonuid:
        print(host, yes)
        passed_listslotportonuid.append(yes)
        i = i + 1
        remaining = len(list_slotportonuid) - i
        print(remaining, 'data lagi')
        print('passed count : ', len(passed_listslotportonuid))
        # =========================== 2
        wesya = 'show gpon remote-onu wan-ip gpon-onu_'+yes
        conn.write(wesya.encode('ascii') + b"\n")
        data_wan = conn.read_until(
            b"IP host ID:", timeout=30).decode('ascii')
        if ('No relate information to show.') in data_wan:
            hasil_wan = onu_wan('notset')
        hasil_wan = onu_wan(data_wan)
        conn.write(b' ')
        conn.write(b'\n')

        print(hasil_wan[0], hasil_wan[1],
              hasil_wan[2], hasil_wan[3], hasil_wan[4])
        updateCust[0].execute('''UPDATE dapel SET username = ?, statuswan = ?, cvlan = ?, currentip = ?, macaddress = ? WHERE slotportonuid = ?''',
                              (hasil_wan[0], hasil_wan[1], hasil_wan[2], hasil_wan[3], hasil_wan[4], yes))
        updateCust[1].commit()

    conn.write(b'exit\n')
    conn.write(b'exit\n')
    conn.write(b'yes\n')
    akhir = time.perf_counter()
    print(akhir-awal)
    # tutup DB
    updateCust[1].close()


def telnetin_customer_pppoe(host, port, username, password, nama_dbnya):
    # =========================
    updateCust = autoupdatedb.updating_customer_file(nama_dbnya)
    # =========================

    conn = Telnet(host, port)
    conn.write(username.encode('ascii') + b"\n")
    conn.write(password.encode('ascii') + b"\n")
    listcummy = ['1/1/1:7']
    conn.write(b'configure terminal\n')
    time.sleep(2)
    list_slotportonuid = cobaceksqliteconnectionpppoe(updateCust[0])
    i = 0  # counter
    for yes in list_slotportonuid:
        print(host, yes)
        passed_listslotportonuid.append(yes)
        i = i + 1
        remaining = len(list_slotportonuid) - i
        print(remaining, 'data lagi')
        print('passed count : ', len(passed_listslotportonuid))

        # =========================== 2
        wesya = 'show gpon remote-onu pppoe gpon-onu_'+yes
        conn.write(wesya.encode('ascii') + b"\n")
        # conn.write(b'show gpon onu detail-info gpon-onu_1/1/1:3\n')
        data_wan = conn.read_until(b"IP host ID:", timeout=1).decode('ascii')
        if ('No relate information to show.') in data_wan:
            hasil_wan = onu_wan('notset')

        hasil_wan = onu_wan(data_wan)
        # print(hasil_wan)
        conn.write(b' ')
        conn.write(b'\n')

        print('pppoe : ', hasil_wan[0], hasil_wan[1],
              hasil_wan[2], hasil_wan[3], hasil_wan[4])
        updateCust[0].execute('''UPDATE dapel SET username = ?, statuswan = ?, cvlan = ?, currentip = ?, macaddress = ? WHERE slotportonuid = ?''',
                              (hasil_wan[0], hasil_wan[1], hasil_wan[2], hasil_wan[3], hasil_wan[4], yes))
        updateCust[1].commit()

    conn.write(b'exit\n')
    conn.write(b'exit\n')
    conn.write(b'yes\n')
    akhir = time.perf_counter()
    print(akhir-awal)
    # tutup DB
    updateCust[1].close()


def telnetin_customer_wan_redaman(host, port, username, password, nama_dbnya):

    # =========================
    updateCust = autoupdatedb.updating_customer_file(nama_dbnya)
    # =========================

    conn = Telnet(host, port)
    conn.write(username.encode('ascii') + b"\n")
    conn.write(password.encode('ascii') + b"\n")
    listcummy = ['1/1/1:7']
    conn.write(b'configure terminal\n')
    time.sleep(2)
    list_slotportonuid = cobaceksqliteredaman(updateCust[0])
    i = 0  # counter
    for yes in list_slotportonuid:
        print(host, yes)
        passed_listslotportonuid.append(yes)
        i = i + 1
        remaining = len(list_slotportonuid) - i
        print(remaining, 'data lagi')
        print('passed count : ', len(passed_listslotportonuid))
        # =========================== 2
        wesya = 'show pon power olt-rx gpon-onu_'+yes
        conn.write(wesya.encode('ascii') + b"\n")
        # conn.write(b'show gpon onu detail-info gpon-onu_1/1/1:3\n')
        data_redaman = conn.read_until(b"(dbm)", timeout=1).decode('ascii')

        hasil_redaman = onu_red(yes, data_redaman)
        print(hasil_redaman)
        conn.write(b' ')
        conn.write(b'\n')

        updateCust[0].execute('''UPDATE dapel SET redamancust = ? WHERE slotportonuid = ?''',
                              (hasil_redaman, yes))
        updateCust[1].commit()

    conn.write(b'exit\n')
    conn.write(b'exit\n')
    conn.write(b'yes\n')
    akhir = time.perf_counter()
    print(akhir-awal)
    # tutup DB
    updateCust[1].close()


def telnetin_customer_wan_equipment(host, port, username, password, nama_dbnya):

    # =========================
    updateCust = autoupdatedb.updating_customer_file(nama_dbnya)
    # =========================

    conn = Telnet(host, port)
    conn.write(username.encode('ascii') + b"\n")
    conn.write(password.encode('ascii') + b"\n")
    listcummy = ['1/1/1:7']
    conn.write(b'configure terminal\n')
    time.sleep(2)
    list_slotportonuid = cobaceksqlite(updateCust[0])
    i = 0  # counter
    for yes in list_slotportonuid:
        print(host, yes)
        passed_listslotportonuid.append(yes)
        i = i + 1
        remaining = len(list_slotportonuid) - i
        print(remaining, 'data lagi')
        print('passed count : ', len(passed_listslotportonuid))
        # =========================== 2
        wesya = 'show gpon remote-onu equip gpon-onu_'+yes
        conn.write(wesya.encode('ascii') + b"\n")
        # conn.write(b'show gpon onu detail-info gpon-onu_1/1/1:3\n')
        data_equip = conn.read_until(b"Chip info:").decode('ascii')

        hasil_equip = onu_equip(data_equip)
        print(hasil_equip)
        time.sleep(1)

        updateCust[0].execute('''UPDATE dapel SET vendorid = ?, version = ?, equipmentid = ? WHERE slotportonuid = ?''',
                              (hasil_equip[0], hasil_equip[1], hasil_equip[2], yes))
        updateCust[1].commit()

    conn.write(b'exit\n')
    conn.write(b'exit\n')
    conn.write(b'yes\n')
    akhir = time.perf_counter()
    print(akhir-awal)
    # tutup DB
    updateCust[1].close()


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


def onu_wan(data1):
    try:
        username = re.search(r'\d+@abece.net', data1)
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

    return username[0], status[1], cvlan, currip, macAddres


def onu_red(onuidnya, data2):
    redamanCust = re.search(rf'{onuidnya}\s*([^\s].*)', data2)
    return redamanCust[1]


def onu_equip(data3):
    vendorID = re.search(r'Vendor ID:\s*([^\s]+)', data3)
    version = re.search(r'Version:\s*([^\s]+)', data3)
    equipmentID = re.search(r'Equipment ID:\s*([^\s]+.*)', data3)

    return vendorID[1], version[1], equipmentID[1]


def cobaceksqliteredaman(cur):
    hasil_null = []
    hasil = cur.execute(
        '''SELECT slotportonuid FROM dapel WHERE phasestate = 'working' and redamancust is null ''').fetchall()
    for yeah in hasil:
        zet = ''.join((yeah))
        hasil_null.append(zet)

    print(hasil_null)
    return hasil_null


def cobaceksqlite(cur):
    hasil_null = []
    hasil = cur.execute(
        '''SELECT slotportonuid FROM dapel WHERE equipmentid is null ''').fetchall()
    for yeah in hasil:
        zet = ''.join((yeah))
        hasil_null.append(zet)

    print(hasil_null)
    return hasil_null


def cobaceksqliteconnectionpppoe(cur):
    hasil_pppoe = []
    hasil1 = cur.execute(
        '''SELECT slotportonuid FROM dapel WHERE connection = 'pppoe' and username is null ''').fetchall()
    for yeah in hasil1:
        zet = ''.join((yeah))
        hasil_pppoe.append(zet)

    print(hasil_pppoe)
    return hasil_pppoe


def cobaceksqliteconnectionwanip(cur):
    hasil_wanip = []
    hasil2 = cur.execute(
        '''SELECT slotportonuid FROM dapel WHERE connection = 'wan-ip' and username is null ''').fetchall()
    for yeah in hasil2:
        zet = ''.join((yeah))
        hasil_wanip.append(zet)

    print(hasil_wanip)
    return hasil_wanip


def getMoreData(self):
    """
    Reads STDOUT, splits on and strips '\r\n'.

    Returns list.
    """
    # 10 means that we're going to timeout after 10 seconds if
    # we don't get any input that satisfies our regex.
    cursor = self.connection.read_until('\r\n', 10)

    # Make sure we have something to work with.
    if len(cursor) > 0:
        for line in cursor.split(','):
            # Sometimes we get empty strings on split.
            if line != '':
                self.data.append(line)
    return self.data


def logDatanya(prosesnya, host):
    cwd = os.getcwd()
    buka = open('{}/onutelnet {}.txt'.format(cwd, host), 'a')
    return buka


# ======================================================>>>> starts here

awal = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    future = executor.submit(telnetin, 'ip1',
                             'host1', 'userip1', 'passip1')
    future1 = executor.submit(telnetin, 'ip2',
                              'host2', 'userip2', 'passsip2')
    future111 = executor.submit(telnetin, 'ip3',
                                'host3', 'userip3', 'passsip3')

    return_value = future.result()
    return_value1 = future1.result()
    return_value11 = future111.result()

    print(return_value[2])
    print(return_value1[2])
    print(return_value11[2])
    while True:
        future2 = executor.submit(telnetin_customer_detail, 'ip1',
                                  'host1', 'userip1', 'passip1', return_value[2])
        future3 = executor.submit(telnetin_customer_detail, 'ip2',
                                  'host2', 'userip2', 'passsip2', return_value1[2])
        future333 = executor.submit(telnetin_customer_detail, 'ip3',
                                    'host3', 'userip3', 'passsip3', return_value11[2])
        try:
            future2.result()
            future3.result()
            future333.result()
            break
        except:
            pass

    while True:
        future41 = executor.submit(telnetin_customer_onu, 'ip1',
                                   'host1', 'userip1', 'passip1', return_value[2])
        future51 = executor.submit(telnetin_customer_onu, 'ip2',
                                   'host2', 'userip2', 'passsip2', return_value1[2])
        future61 = executor.submit(telnetin_customer_onu, 'ip3',
                                   'host3', 'userip3', 'passsip3', return_value11[2])
        try:
            future41.result()
            future51.result()
            future61.result()
            break
        except:
            pass

    while True:
        future4 = executor.submit(telnetin_customer_wan, 'ip1',
                                  'host1', 'userip1', 'passip1', return_value[2])
        future5 = executor.submit(telnetin_customer_wan, 'ip2',
                                  'host2', 'userip2', 'passsip2', return_value1[2])
        future6 = executor.submit(telnetin_customer_wan, 'ip3',
                                  'host3', 'userip3', 'passsip3', return_value11[2])
        try:
            future4.result()
            future5.result()
            future6.result()
            break
        except:
            pass

    while True:
        future44 = executor.submit(telnetin_customer_pppoe, 'ip1',
                                   'host1', 'userip1', 'passip1', return_value[2])
        future55 = executor.submit(telnetin_customer_pppoe, 'ip2',
                                   'host2', 'userip2', 'passsip2', return_value1[2])
        future66 = executor.submit(telnetin_customer_pppoe, 'ip3',
                                   'host3', 'userip3', 'passsip3', return_value11[2])
        try:
            future44.result()
            future55.result()
            future66.result()
            break
        except:
            pass

    while True:
        future6 = executor.submit(telnetin_customer_wan_redaman, 'ip1',
                                  'host1', 'userip1', 'passip1', return_value[2])
        future7 = executor.submit(telnetin_customer_wan_redaman, 'ip2',
                                  'host2', 'userip2', 'passsip2', return_value1[2])
        future61 = executor.submit(telnetin_customer_wan_redaman, 'ip3',
                                   'host3', 'userip3', 'passsip3', return_value11[2])
        try:
            future6.result()
            future7.result()
            future61.result()
            break
        except:
            pass

    while True:
        future8 = executor.submit(telnetin_customer_wan_equipment, 'ip1',
                                  'host1', 'userip1', 'passip1', return_value[2])
        future9 = executor.submit(telnetin_customer_wan_equipment, 'ip2',
                                  'host2', 'userip2', 'passsip2', return_value1[2])
        future00 = executor.submit(telnetin_customer_wan_equipment, 'ip3',
                                   'host3', 'userip3', 'passsip3', return_value11[2])
        try:
            future8.result()
            future9.result()
            future00.result()
            break
        except:
            pass

    autoupdatedb.updating_file(
        return_value[2], return_value[3])
    time.sleep(1)
    autoupdatedb.updating_file(
        return_value1[2], return_value1[3])
    time.sleep(1)
    autoupdatedb.updating_file(
        return_value11[2], return_value11[3])

akhir = time.perf_counter()
print(akhir-awal)
