import mysql.connector
import os
import datetime
from difflib import SequenceMatcher
import json


# surfsql.py inneholder funksjoner bl.a for å hente ut tider ifra surfdatabasen basert på kriteriene: 
# Beste tid på alle maps (qmode: all), de 10 beste tidene på et spesifikt map (qmode: map) eller alle tidene til en surfer (qmode: usr)
# Presiserer du map, sjekker den om mapet eksisterer i mapcycle, og kjører så en spørring


# Get config
f = open("config.json", "r")
config = f.read()
config = json.loads(config)

# For loop setter hver key i config.json som en varibel med value .
for setting, v in config.items():
    globals()[setting] = str(v)

def runQuery(arg, arg2=0):
    ddb = surfdb
    if arg2:
        ddb = trackdb
    mydb = mysql.connector.connect(
        host=dbhost,
        user = dbuser,
        password=dbpw,
        database=ddb
        )  
    mycursor = mydb.cursor()
    mycursor.execute(arg)
    respons= mycursor.fetchall()
    if mycursor.rowcount < 1:
        return []
    return respons

# disse lager lesbar tid av sekunder:

def formatTime(time, arg=1): # Lag en string med minutt:sekund:millisekund hvor getmil finner millieskundet litt annerledes enn de andre
    if arg == 1:

        milliseconds = (str(time).partition(".")[2])[:3]
        time = time % (24 * 3600)
        hour = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time

        minutes = str(int(minutes))
        seconds = str(int(seconds))
        minutes = minutes.zfill(2)
        seconds = seconds.zfill(2)
        milliseconds = milliseconds.zfill(3)

        return str(("%s:%s:%s" % (minutes, seconds, milliseconds)))

    else:        
        day = time // (24 * 3600)
        time = time % (24 * 3600)
        hour = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time

        day = str(int(day))
        hour = str(int(hour))
        minutes = str(int(minutes))
        seconds = str(int(seconds))
        hour = hour.zfill(2)
        day = day.zfill(3)
        minutes = minutes.zfill(2)
        seconds = seconds.zfill(2)

        return ("%s:%s:%s:%s" % (day, hour, minutes, seconds))

# Hent liste over maps. Denne spør ikke databasen da maps som ikke lenger er i bruk kan refereres til der.
def getmaps():
    with open(csgofolder + 'maplist.txt', 'r') as a_file:       
        maplist = [line.strip() for line in a_file]
        a_file = open(csgofolder + "maplist.txt", "r")
        a_file.close()
        return maplist

# Funksjoner for å hente total tid en bruker har vært koblet til serveren. Tracket av sourcemod plugin i tracker databasen.
def timetopten():
    global jDict
    jDict = {}
    sql = f"""select steamid, name, TimePlayed from TimeTracker order by TimePlayed desc limit 10;"""
     
    result = runQuery(sql,1)
    i = 0
    for item in result:
        jDict[i] = {'steamid': str(item[0]), 'name' : item[1], 'time' : formatTime(item[2],0)}
        i += 1
    return jDict

def timeplayed(arg):
    sql = f"""select steamid, TimePlayed from TimeTracker where steamid = '{arg}';"""
    timequery = runQuery(sql,1)
    timespent = formatTime(float(timequery[0][1]), 0)
    return str(timespent)

# Funksjon for å hente ut alle server rekorder, top 10 rekorder for et spesifikt map eller rekorder satt av en bruker.
def getrecords(arg=''):
        listrec = []
        totalrec= []
        toprecs = 0
        maplist = getmaps()
        userlist = []
        if f"surf_{arg}" in maplist:
            arg = "surf_" + arg

        if arg in maplist:
            qmode = "map"
            jDict = {}
            sql = f"""select steamid, name, mapname, runtimepro from ck_playertimes  where mapname = '{arg}' order by runtimepro asc limit 10;"""
            result = runQuery(sql)
            
            i = 0
            for item in result:
                if item[3]:
                    jDict[i] = {'steamid': str(item[0]), 'name' : item[1], 'mapname': item[2], 'time' : formatTime(item[3])}
                i += 1

            

        elif arg == "":
            qmode = "all"
            jDict = {}
            i = 0
            for item in maplist:  
                sql = f"""select steamid, name, mapname, runtimepro from (select * from ck_playertimes order by mapname desc, runtimepro desc) x where mapname='{item}' group by mapname;"""
                record = runQuery(sql)
                if not record == []:
                    #print (str(record[0][3]))
                    jDict[i] = {'steamid': str(record[0][0]), 'name' : record[0][1], 'mapname': record[0][2], 'time' : formatTime(record[0][3])}   
                i += 1

        else:
            ratiodict = {}
            qmode = "usr"
            
            sql = f"""select upper(name), steamid from ck_playertimes;"""
            userlist = runQuery(sql)
            arg = arg.upper()

                                    # Sjekk om brukeren er i lista, om ikke finn nærmeste match:
            if arg not in userlist:
                for item in userlist:
                    compname = (item[0])
                    seq = SequenceMatcher(a=compname, b=arg)
                    ratio = seq.ratio()
                    if ratio >= 0.4:
                        ratiodict[compname] = ratio

                arg = max(ratiodict, key=ratiodict.get)
                

            sql = f"""select steamid, name, mapname, runtimepro from ck_playertimes where steamid = (select steamid from ck_playertimes where upper(name) = upper('{arg}') limit 1);"""
            respons = runQuery(sql)
            steamid = respons[0][0]
            timep = timeplayed(steamid)
            i = 0
            jDict = {}
            for item in respons:
                jDict[i] = {'steamid': str(item[0]), 'name' : item[1], 'mapname': item[2], 'time' : formatTime(item[3]), 'timeplayed' : str(timep)}
                i += 1

        jDict['qmode'] = qmode
        return jDict
#            for item in maplist:
#              
#                sql = f"""select mapname, steamid, runtimepro from (select * from ck_playertimes order by mapname desc, runtimepro desc) x where mapname='{item}' group by mapname;"""
#                respons = runQuery(sql)

#                if not respons == []:
#                    totalrec.extend(respons[0][1])  

#           for item in totalrec:
#               if (item[1] == steamid):
#                   toprecs += 1
#            jDict['toprecords'] = toprecs
        




