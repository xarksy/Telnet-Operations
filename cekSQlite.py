import sqlite3

def cobaceksqliteredaman(cur):
    hasil_null = []
    hasil = cur.execute(
        '''SELECT slotportonuid FROM dapel WHERE phasestate = 'working' and redamancust is null ''').fetchall()
    for cariData in hasil:
        datanyanih = ''.join((cariData))
        hasil_null.append(datanyanih)

    print(hasil_null)
    return hasil_null


def cobaceksqlite(cur):
    hasil_null = []
    hasil = cur.execute(
        '''SELECT slotportonuid FROM dapel WHERE equipmentid is null ''').fetchall()
    for cariData in hasil:
        datanyanih = ''.join((cariData))
        hasil_null.append(datanyanih)

    print(hasil_null)
    return hasil_null


def cobaceksqliteconnectionpppoe(cur):
    hasil_pppoe = []
    hasil1 = cur.execute(
        '''SELECT slotportonuid FROM dapel WHERE connection = 'pppoe' and username is null ''').fetchall()
    for cariData in hasil1:
        datanyanih = ''.join((cariData))
        hasil_pppoe.append(datanyanih)

    print(hasil_pppoe)
    return hasil_pppoe


def cobaceksqliteconnectionwanip(cur):
    hasil_wanip = []
    hasil2 = cur.execute(
        '''SELECT slotportonuid FROM dapel WHERE connection = 'wan-ip' and username is null ''').fetchall()
    for cariData in hasil2:
        datanyanih = ''.join((cariData))
        hasil_wanip.append(datanyanih)

    print(hasil_wanip)
    return hasil_wanip


def usernameKelewat(cur):
    hasil_wanip = []
    hasil2 = cur.execute(
        '''SELECT slotportonuid FROM dapel WHERE username = 'Password:' ''').fetchall()
    for cariData in hasil2:
        datanyanih = ''.join((cariData))
        hasil_wanip.append(datanyanih)

    print(hasil_wanip)
    return hasil_wanip