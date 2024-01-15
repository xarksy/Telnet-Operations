import sqlite3
import os
from datetime import datetime
import shutil


# Function to create directory if it does not exist
def create_directory(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)

# Creating necessary directories
create_directory("rekapan")
create_directory("hasil")


def saving_file(ipnya, portnya):
    ipnya = ipnya.replace('.', '-')
    filename_hasilssh = r'rekapan/' + ipnya + portnya + ' ' + \
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
            vendorid text, version text, equipmentid text, connection text)  ''')

    return cur, con, filename_hasilssh, ipnya, portnya


def updating_file(filename, ipnya, portnya):
    try:
        os.remove("hasil/" + ipnya + portnya + " main.db")
    except:
        pass
    wew = shutil.copy2(filename, 'hasil')
    print(wew)
    new_file = os.path.join("hasil/", ipnya + portnya + " main.db")
    os.rename(filename, new_file)
    shutil.copy2(wew, 'rekapan')
    os.remove(wew)

    return wew


def updating_customer_file(filename):
    con = sqlite3.connect(filename)
    cur = con.cursor()

    return cur, con
