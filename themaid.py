# Link for token: https://discordapp.com/oauth2/authorize?client_id= ***CLIENTID*** &scope=bot&permissions=8

import asyncio
from discord.ext import commands
import discord as discord
import random
import os
import json
import requests


intents = discord.Intents.all()

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
adminid = str(config['adminid'])
welcomemessage = str(config['welcome'])

terplist =["Terped up on the scene, keepin it Crispy Creme.", "Terp Nation, Terp Motivation.", "I don't speak English, I speak Terpanese.", "Oh we got sum right here, that Terp shit, that's real shit!"]
lastmsg = ""

bot = commands.Bot(command_prefix=bprefix, intents = intents, case_insensitive=True)

def parsemsg(raw, obj):
    try:
        username = obj.author.display_name
        servername = obj.author.guild.name
    except:
        username = obj.display_name
        servername = obj.guild.name

    msg = raw.replace("#user#", username)
    msg = msg.replace("#serv#", servername)

    return msg 

def getstockprice(ticker):
    x = requests.get('http://api.marketstack.com/v1/intraday/latest?access_key=a39f5913720ae27952e5a293cf7d3ec9&symbols=' + ticker.upper())
    s = x.json()
    return (s['data'][0]['last'])

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

@bot.event
async def on_message(message):
    global lastmsg
    msg = ""

    if message.author == bot.user:
        return

    if 'TERP' in (str(message.content)).upper():
        
        while msg != lastmsg:
            msg = str(random.choice(terplist))
            lastmsh = msg

        await message.channel.send(msg)


    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
            global welcomemessage
            response = parsemsg(welcomemessage, member)
            await member.send(response)

@bot.command()
async def h(ctx):
    try:
        channelname =  ctx.channel.name
    except:
        channelname = ""
    try:
        roles = str(ctx.message.author.roles)
    except:
        roles = ""

    if channelname == "admin" or adminid in roles:
        
        embedVar = discord.Embed(title="Help Menu: ", description="Admin commands: \n\n-", color=0x6B2121)
        embedVar.add_field(name="!h", value="Shows this menu", inline=False)
        embedVar.add_field(name="!r", value="Shows the surf leaderboards. Add map or player as a parameter for details. Example: **!r surf_pantheon**", inline=False)
        embedVar.add_field(name="!m", value="Shows current installed maps.", inline=False)
        embedVar.add_field(name="!tp", value="Shows top ten users based on total connection time.", inline=False)
        embedVar.add_field(name="!s", value="Shows the status of the server, including connected players.", inline=False)
        embedVar.add_field(name="!w", value="""Shows or sets the discord Welcome message. Example: **!w "Welcome to #serv#, #user#!"**""", inline=False)       
        embedVar.add_field(name="!cmd **console command**", value="Runs a console command on the server. Example: **!cmd changelevel surf_map**", inline=False)
        await ctx.send(embed=embedVar)
    
    else:
        embedVar = discord.Embed(title="Help Menu: ", description="Commands: \n\n-", color=0x6B2121)
        embedVar.add_field(name="!h", value="Shows this menu", inline=False)
        embedVar.add_field(name="!r", value="Shows the surf leaderboards. Add map or player as a parameter for details. Example: **!r surf_pantheon** or **!r someuser**", inline=False)
        embedVar.add_field(name="!m", value="Shows current installed maps.", inline=False)
        embedVar.add_field(name="!tp", value="Shows top ten users based on total connection time.", inline=False)
        embedVar.add_field(name="!s", value="Shows the status of the server, including connected players.", inline=False)
        await ctx.send(embed=embedVar)
  

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
async def kurs(ctx, arg=''):
    response = ""
    if arg == '':
        await ctx.send("```No ticker specified.```")

    else:
        try:
            price = str(getstockprice(arg))
            response = "The price of " + arg.upper() +" is $" + price
        except:
            price = "```No data found.```"

    await ctx.send(response)

        
@bot.command()
async def d(ctx, arg=''):
        try:
            channelname =  ctx.channel.name
        except:
            channelname = ""
        try:
            roles = str(ctx.message.author.roles)
        except:
            roles = ""

        if channelname == "admin" or adminid in roles:
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
            await ctx.send ("```Not admin```")

@bot.command()
async def tp(ctx):
    getstat = requests.get(apidomain + "/tp")
    response = getstat.text
    await ctx.send("```" + "Total time played on server\n\n" + response + "```")
                                   
@bot.command()
async def cmd(ctx, arg1, arg2=''):
    try:
        channelname =  ctx.channel.name
    except:
        channelname = ""
    try:
        roles = str(ctx.message.author.roles)
    except:
        roles = ""

    if channelname == "admin" or adminid in roles:
        cmd = arg1 + " " + arg2
        os.system('sh sendmsg.sh ' + cmd )
        f = open('tmuxout.log')
        response = f.read()
        if len(response) > 1000:
            response = response[-1000]
        f.close()
        await ctx.send("```" + response + "```")
    else:
        await ctx.send ("```Not admin```")

@bot.command()
async def w(ctx, arg1='0'):
    global welcomemessage

    try:
        channelname =  ctx.channel.name
    except:
        channelname = ""
    try:
        roles = str(ctx.message.author.roles)
    except:
        roles = ""

    if channelname == "admin" or adminid in roles:
        if arg1 == "0":
            await ctx.send("```This is the current welcome message:```")

            response = parsemsg(welcomemessage, ctx)
            await ctx.send(response)

        else:
            welcomemessage = arg1
            await ctx.send("```New welcome message set```")
    else:
        await ctx.send ("```Not admin```")


bot.run(dctoken)
         
