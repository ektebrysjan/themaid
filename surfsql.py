import mysql.connector
import os
import datetime
from difflib import SequenceMatcher
import json

# surfsql.py inneholder funksjoner bl.a for å hente ut tider ifra surfdatabasen basert på kriteriene: 
# Beste tid på alle maps (qmode: all), de 10 beste tidene på et spesifikt map (qmode: map) eller alle tidene til en surfer (qmode: usr)
# Presiserer du map, sjekker den om mapet eksisterer i mapcycle, og kjører så en spørring

tidlis = []
qmode = ""
maplist = []
toprecs = 0
steamid = ""
usermatch = True

# Get config
f = open("config.json", "r")
config = f.read()
config = json.loads(config)

csgofolder = str(config['csgofolder'])
dbhost =  str(config['dbhost'])
dbuser = str(config['dbuser'])
dbpw = str(config['dbpw'])
surfdb = str(config['surfdb'])
trackdb = str(config['trackdb'])

# padding funksjon for å lage jevne kolonner i discord meldinger
def pad(word, len_=30, spacer=' '):
    return word + (len_ - len(word)) * spacer

# disse lager lesbar tid av sekunder:

def gettime(time, arg=1): # Lag en string med minutt:sekund:millisekund hvor getmil finner millieskundet litt annerledes enn de andre
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
    #return ("" + str(minutes) + ":" + str(seconds) + ":" + milliseconds)
        

# Hent liste over maps. Denne spør ikke databasen da maps som ikke lenger er i bruk kan refereres til der.
def getmaps():
    with open(csgofolder + 'maplist.txt', 'r') as a_file:
        
        maplist = [line.strip() for line in a_file]
        a_file = open(csgofolder + "maplist.txt", "r")
        a_file.close()
        return maplist

# Funksjoner for å hente total tid en bruker har vært koblet til serveren. Tracket av sourcemod plugin i tracker databasen.
def timetopten():
    mydb = mysql.connector.connect(
        host=dbhost,
        user = dbuser,
        password=dbpw,
        database=trackdb
        )  
    mycursor = mydb.cursor()
    sql = f"""select name, steamid, TimePlayed from TimeTracker order by TimePlayed desc limit 10;"""
     
    mycursor.execute(sql)
    query = mycursor.fetchall()
    return query

def timeplayed(arg):

    mydb = mysql.connector.connect(
        host=dbhost,
        user = dbuser,
        password=dbpw,
        database=trackdb
        )  
    mycursor = mydb.cursor()
    sql = f"""select steamid, TimePlayed from TimeTracker where steamid = '{arg}';"""
     
    mycursor.execute(sql)
    timequery = mycursor.fetchall()
    timespent = gettime(float(timequery[0][1]), 0)
    return str(timespent)


# Funksjon for å hente ut alle server rekorder, top 10 rekorder for et spesifikt map eller rekorder satt av en bruker.
def getrecords(spef):

    global tidlis, qmode, toprecs, steamid, usermatch
    usermatch = True

    mydb = mysql.connector.connect(
        host=dbhost,
        user = dbuser,
        password=dbpw,
        database=surfdb
        )  
    mycursor = mydb.cursor()

    maplist = getmaps()
    tidlis = []
    listrec = []
    totalrec= []
    toprecs = 0
    steamid = ""
    qmode = ""
    
    if (spef in maplist):           # Dersom argumentet (spef) er i maplisten, hent top 10 rekorder på det mappet
    
        qmode = "map"
        sql = f"""select mapname, name, runtimepro from ck_playertimes  where mapname = '{spef}' order by runtimepro asc limit 10;"""
        mycursor.execute(sql)
        record = mycursor.fetchall()
        
        for x in range(len(record)):
            
            tidlis.append(gettime(float(record[x][2])))
        listrec = record
                           
    
    elif (spef == ""):              # Om ikke map eller bruker spesifisert (spef) list alle maprekorder
        qmode = "all"
        for item in maplist:
                
            sql = f"""select mapname, name, runtimepro from (select * from ck_playertimes order by mapname desc, runtimepro desc) x where mapname='{item}' group by mapname;"""
            mycursor.execute(sql)
            record = mycursor.fetchall()
            
            if not record == []:
                tidlis.append(gettime(float(record[0][2]))) 
                listrec.extend(record)
                   
    else:                           # Om ingen av de to over, anta at det er et brukernavn og sjekk evt etter lignende:
            qmode = "usr"
            ratiodict = {}
            sql = f"""select upper(name), steamid from ck_playertimes;"""
            mycursor.execute(sql)
            userlist = mycursor.fetchall()
            spef = spef.upper()

                                    # Sjekk om brukeren er i lista, om ikke finn nærmeste match:
            if spef not in userlist:
                usermatch = False
                for item in userlist:
                    compname = (item[0])
                    seq = SequenceMatcher(a=compname, b=spef)
                    ratio = seq.ratio()
                    if ratio >= 0.5:
                        ratiodict[compname] = ratio

                max_key = max(ratiodict, key=ratiodict.get)
                spef = max_key
                                    # Søk opp navnet og hent alle rekorder med korresponderende steamid:

            sql = f"""select mapname, name, runtimepro, steamid from ck_playertimes where steamid = (select steamid from ck_playertimes where upper(name) = upper('{spef}') limit 1);"""
            mycursor.execute(sql)
            record = mycursor.fetchall()
            listrec = record
            steamid = record[0][3]

            for x in range(len(record)):
            
                tidlis.append(gettime(float(record[x][2])))
            listrec = record
                                    # Tell antall serverrekorder for denne brukeren:
            for item in maplist:
                
                sql = f"""select mapname, steamid, runtimepro from (select * from ck_playertimes order by mapname desc, runtimepro desc) x where mapname='{item}' group by mapname;"""
                mycursor.execute(sql)
                record = mycursor.fetchall()
                
                if not record == []:
                    totalrec.extend(record)  

            for item in totalrec:
                if (item[1] == steamid):
                    toprecs += 1
            
    return listrec

# Lag discord-vennlig table og hent ut maps og navn fra getrecords records og riktig formattert tid ifra global tidlis. Sjekker qmode for formattering. Burde egentlig gjøres i api'et.
def maketable(arg):
    global tidlis, qmode, toprecs, steamid, usermatch
    tablestr = ""
    
    table = getrecords(arg)
    

    if qmode == "all":
        altitle = """__All server records by map:__"""
        title = pad("Map") + pad("Player") + pad("Time")

        for x in range(len(table)):
            row = pad(str(table[x][0])) + pad(str(table[x][1])) + pad(str(tidlis[x]))
            tablestr = (tablestr + row + "\n")
    
    elif qmode == "usr":
        
        altitle = ""

        try:
            timespent = timeplayed(steamid)
        except:
             timespent = "No data"

        if usermatch == False:
            altitle = "Could not find user, fetching nearest match:\n"

        altitle = altitle + """__**""" + str(table[0][1]) + """'s** map records:__\n\nTotal server records: """ + str(toprecs) + """\nTotal time spent on server: """ + str(timespent)
        title = pad("Map") + pad("Time")
        for x in range(len(table)):
            row = pad(str(table[x][0])) + pad(str(tidlis[x]))
            tablestr = (tablestr + row + "\n")
    
    elif qmode == "map":
        #map = str(table[0][0])
        altitle = """__Best times on: **""" + str(table[0][0]) + """**:__"""
        title = pad("Place") + pad("Player") + pad("Time")
        for x in range(len(table)):
        
            player = str(table[x][1])                                               # Hent navn for denne loopen x
            player = (player[:18] + '...') if len(player) > 18 else player          # Er navnet lenger enn 18, forkort
            
            row = pad(("# " + str(x+1))) + pad(player) + pad(str(tidlis[x]))
            tablestr = (tablestr + row + "\n")
           
    return (altitle + "\n\n" + "```" + title + "\n \n" + tablestr + "```")

