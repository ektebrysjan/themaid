# Link for token: https://discordapp.com/oauth2/authorize?client_id= ***CLIENTID*** &scope=bot&permissions=8

import asyncio
from discord.ext import commands
import os
import json
import requests

# Get config
f = open("config.json", "r")
config = f.read()
config = json.loads(config)
adomain = str(config['domain']).replace('https://', '')
aport = str(config['port'])
dctoken = str(config['dctoken'])
csgofolder = str(config['dctoken'])
mapsfolder = str(config['mapsfolder'])
fastdlfolder = str(config['fastdlfolder'])
domain =  str(config['domain'])
apidomain = domain + ":" + aport
bprefix  = str(config['prefix'])

bot = commands.Bot(command_prefix=bprefix)

def deletemap(map):
        ex = []
        e = 0
        remfil = 0
        errormsg = ""

        try:
            with open(csgofolder + 'maplist.txt', 'r') as a_file:            
                maplist = [line.strip() for line in a_file]
                a_file = open(csgofolder + "maplist.txt", "r")
            a_file.close()
        except:
            e = 1
            ex.append("Open maplist - Failed")
        else:
            ex.append("Open maplist - Sucess")

        try:
            maplist.remove(map)
        except:
            e = 1
            ex.append("Remove map from list - Failed -- Not in maplist")
        else:
            ex.append("Remove map from list - Success")

        try:
            newfile = open(csgofolder + "maplist.txt", "w")
            for item in maplist:
                newfile.write("%s\n" % item)
            newfile.close()
        except:
            e = 1
            ex.append("Create temp - Failed")
        else:
            ex.append("Create temp - Success")
            
        try:          
            os.system('rm -f ' + csgofolder + 'mapcycle.txt')
        except:
            e = 1
            ex.append("Delete old maplist - Failed")
        else:
            ex.append("Delete old maplist - Success")
        
        try:
            os.system('cp ' + csgofolder + 'maplist.txt ' + csgofolder + 'mapcycle.txt')
        except:
            e = 1
            ex.append("Create Maplist - Failed")
        else:
            ex.append("Create maplist - Success")

        remfil = os.system('rm ' + mapsfolder + map + '.bsp')
        if not remfil == 0:
            e = 1
        ex.append("Remove bsp file - Failed code: " + str(remfil))
        
        remfill = 0

        remfil = os.system('rm ' + fastdlfolder + map + '.bsp.bz2')
        if not remfil == 0:
            e = 1
        ex.append("Remove fastdl file - Failed code: " + str(remfil))
        
        for er in ex:
            errormsg = (errormsg + er + "\n")
        
        if e:
            return ("**Something went wrong.**\n\n Errorlog:\n```" + errormsg + "```")
        else:
            return ("```" + map + " has been removed from the server```")

@bot.event
async def on_ready():
    print(f"Jeg har logga inn som {bot.user}")
    global n, e, u
    
@bot.command()
async def h(ctx):
    if ctx.channel.name == "admin":
        
        await ctx.send("""         
Hello, I'm **The Maid.** I keep it tidy in Mike's Apartment.
                           
**Commands:**
**!h** shows this menu.
**!r** shows the surf leaderboards. Add map or player as a parameter for details. Example: **!r surf_pantheon**
**!m** shows current installed maps.
**!tp** shows top ten users based on total connection time
**!d surf_mapname** Removes a map from the server.
**!s** shows the status of the server, including connected players.
**!cmd consolecommand** runs a console command on the server. Example: **!cmd changelevel surf_map**                           
 """)
    else:
        await ctx.send("""         
Hello, I'm **The Maid.** I keep it tidy in Mike's Apartment.

**Commands:**
**!h** shows this menu.
**!r** shows the surf leaderboards. Add map or player as a parameter for details. Example: **!r surf_pantheon**
**!m** shows current installed maps.
**!tp** shows top ten users based on total connection time
**!s** shows the status of the server, including connected players.

For **admin** commands, type !h in #admin.
""")

@bot.command()
async def m(ctx):
    mapmesg = ""
    mapson = requests.get(apidomain + "/gm")
    maplist = json.loads(mapson.text)
    for map in maplist:
        mapmesg = mapmesg + str(map) + "\n"
   
    await ctx.send("__List of active maps:__" + "\n" + "```" + mapmesg + "```")

@bot.command()
async def s(ctx):

    getstat = requests.get(apidomain + "/st")
    response = getstat.text
    await ctx.send("```" + response + "```")
            
@bot.command()
async def r(ctx, arg=''):
    recson = requests.get(apidomain + "/lb?arg=" + arg)
    response = (str(recson.text))
    await ctx.send(response)

        
@bot.command()
async def d(ctx, arg=''):
        if ctx.channel.name == "admin":
            mapson = requests.get(apidomain + "/gm")
            maplist = json.loads(mapson.text)

            if  arg == '':
                await ctx.send("```No map specified```")
                
            elif arg not in maplist:
                await ctx.send("```Map does not exist. Type !m for active maps```")
            
            else:
                delmap = deletemap(arg)
                
                await ctx.send(delmap)
        else:
            await ctx.send ("```Not in admin channel```")

@bot.command()
async def tp(ctx):
    getstat = requests.get(apidomain + "/tp")
    response = getstat.text
    await ctx.send("```" + "Total time played on server\n\n" + response + "```")
                                   
@bot.command()
async def cmd(ctx, arg1, arg2=''):
    if ctx.channel.name == "admin":
        cmd = arg1 + " " + arg2
        os.system('sh sendmsg.sh ' + cmd )
        f = open('tmuxout.log')
        response = f.read()
        if len(response) > 1000:
            response = response[-1000]
        f.close()
        await ctx.send("```" + response + "```")
    else:
        await ctx.send ("```Not in admin channel```")
                

bot.run(dctoken)
         
