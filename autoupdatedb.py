import sqlite3
import os
import re
from datetime import datetime
import shutil


current_dir = os.getcwd()

# checking if the directory demo_folder2
# exist or not.
if not os.path.isdir("rekapan"):
    os.makedirs("rekapan")

if not os.path.isdir("hasil"):
    os.makedirs("hasil")


def saving_file(ipnya):
    ipnya = ipnya.replace('.', '-')
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
            vendorid text, version text, equipmentid text, connection text)  ''')

    return cur, con, filename_hasilssh, ipnya


def updating_file(filename, ipnya):
    try:
        os.remove("hasil/" + ipnya + " main.db")
    except:
        pass
    wew = shutil.copy2(filename, 'hasil')
    print(wew)
    new_file = os.path.join("hasil/", ipnya + " main.db")
    os.rename(filename, new_file)
    shutil.copy2(wew, 'rekapan')
    os.remove(wew)

    return wew


def updating_customer_file(filename):
    con = sqlite3.connect(filename)
    cur = con.cursor()

    return cur, con
