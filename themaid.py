# Link for token: https://discordapp.com/oauth2/authorize?client_id= ***CLIENTID*** &scope=bot&permissions=8

import asyncio
from discord.ext import commands
import discord as discord
import random
import os
import json
import time
import changename as changename
import openai
import requests

openai.api_key = ""
convolist = []
def itBot():
    global convolist
    print("Initializing conversation history")
    convolist = ["The Maid is an overly entusiastic cool bot that answers questions and writes like a skater:", "You: How many pounds are in a kilogram?", "Huh? oh yeah dude 2.2 pounds is like a kilogram, man, crazy!", "You: What does HTML stand for?", "Aw man I just read about that dude, that stuff is wildin out fascinating, man, legit stuff! It's HyperText Markup Language, man, old trusty! Boom boom! It's kinda like the building blocks you know, the old school, that biggie! Lord have mercy! far out!",  "You: How many centimeters are in one meter", "Boy you better believe it's Straight up on hundred, dawg. Like, the metric system doesn't mess around, bro, they out here fightin each day, yahurrd?!", "You: What is the meaning of life?", "Live and let live, man! All you need is love." ]

itBot()

intents = discord.Intents.all()

# Get config
f = open("config.json", "r")
config = f.read()


config = json.loads(config)

# For loop setter hver key som en varibel med value .
for setting, v in config.items():
    globals()[setting] = str(v)

# Variables:
# aport - port for apiservice
# dctoken - token for dcbot
# csgofolder - where csgo is located
# mapsfolder - where maps are located
# fastdlfolder - webhosted folder for fastdl of maps
# domain - domain name
# bprefix - bot prefix, standard "!"
# adminid - string or number distinguising the admin discord channel.
# welcomemessage - message to new discord server users.
# accesskey - api token for stock api
adomain = 'https://' + domain
apidomain = adomain + ":" + aport
terplist = ["It was a Terpy Terpy day!", "Whole lotta Terp shiet.", "Terped up, ya know, on the scene keepin it Crispy Creme.", "Terp Motivation, Terp Elevation.", "I don't speak English, I speak Terpanese.", "Oh we got sum right here, that Terp shit, that's real shit!"]
mootUsers = {}
bot = commands.Bot(command_prefix=bprefix, intents = intents, case_insensitive=True)



#check if request is remind-related
def isRemind(req):
    keywords = ["remind me", "let me know", "message me", "minn meg på", "kan du huske", "husk", "send meg en", "pm meg", "msg me", "minne" "remember"]
    score = 0

    for i in keywords:
        if i in req:
            score += 1
    
    if score >= 1:
        return True
    else:
        return False
    




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

def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values

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

    if message.author == bot.user:
        return

   # print(message.author)
    if message.author in mootUsers:
        await message.delete()
        return


    if 'MOOT' in (str(message.content)).upper():
        navn = message.content
        navn = navn.replace('moot','')
        await message.delete()


        if navn in mootUsers:
            mootUsers.pop(navn)
            await message.author.send("unmooted " + navn)
        else:
            mootUsers[navn] = message.author.display_name

            await message.author.send("mooted " + message.author.display_name)


    if 'TERP' in (str(message.content)).upper():
        
        msg = str(random.choice(terplist))
        lastmsg = msg

        await message.channel.send(msg)

#gjør narr av navnet
    if '1HEI ' in (str(message.content)).upper():
        navnn = message.content
        navnn = navnn.replace('1hei ','')
        await message.delete()
        await message.channel.send("heI jEg hetEr " + navnn)

    
       # await message.channel.send("heI jEg hetEr " + navn)

    await bot.process_commands(message)

## Welcome message should be turned on or off based on which server it is in. no system for that yet so no welcome message.

#@bot.event
#async def on_member_join(member):
#            global welcomemessage
#            response = parsemsg(welcomemessage, member)
#            await member.send(response)

## HELP MENU
@bot.command()
async def h(ctx, arg1=""):

            ##Try these in case commands are picked up in private messages, making the channel name var empty
    try:
        channelname =  ctx.channel.name
    except:
        channelname = ""
    try:
        roles = str(ctx.message.author.roles)
    except:
        roles = ""

## Here I should add a parameter in the json config for a list of admin users instead, and a command to add and remove admins for the bot.

    if (channelname == "admin" or str(ctx.author) == "mikE#2164" or adminid in roles) and arg1 == "adm":
        
        embedVar = discord.Embed(title="Help Menu: ", description="Admin commands: \n\n-", color=0x6B2121)
        embedVar.add_field(name="!h", value="Shows this menu", inline=False)
        embedVar.add_field(name="!r", value="Shows the surf leaderboards. Add map or player as a parameter for details. Example: **!r surf_pantheon**", inline=False)
        embedVar.add_field(name="!m", value="Shows current installed maps.", inline=False)
        embedVar.add_field(name="!tp", value="Shows top ten users based on total connection time.", inline=False)
        embedVar.add_field(name="!s", value="Shows the status of the server, including connected players.", inline=False)
        embedVar.add_field(name="!w", value="""Shows or sets the discord Welcome message. Example: **!w "Welcome to #serv#, #user#!"** NOT ACTIVATED""", inline=False)       
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
    getmaps = requests.get(apidomain + "/gm?m=dc")
    mapmesg = getmaps.text

@bot.command()
async def purge(ctx, arg):
    if ctx.author.id == 237681368606310400:
        print(int(arg))
        await ctx.channel.purge(limit=int(arg)+1)


@bot.command()
async def q(ctx, *, arg ="hello"):
    global convolist
    rol = ctx.author.roles
    user = ctx.author.id    
    channel = ctx.channel.name

    print(user, channel)
    
    if "botasker" not in str(rol):
        await ctx.send("Shut up, pencil dick")

    else:

        convolist.append(arg + '\n')
        startprompt = '\n'.join(convolist)

        
    



        
        
        if isRemind(arg):
            response2 = openai.Completion.create(
            model="text-davinci-003",
            prompt="is this text a request to be reminded about something? If so answer me what they need to be reminded about and the time they want to be reminded HH:MM:SS format, in Norwegian time. The text: " + arg + ". The text should only contain and what they need to be reminded about and the time, separated with a comma.",
            max_tokens=1000,
            temperature=0,
            )

            resp2 = response2["choices"][0]["text"]

            if "NO" in resp2.upper():
                print("nope")

            else:
                await ctx.send(resp2.split(","))
        else:


            response = openai.Completion.create(
            model="text-davinci-003",
            prompt=startprompt,
            max_tokens=1000,
            temperature=0.9,
            )

            resp = response["choices"][0]["text"]
            await ctx.send(resp[1:])
            convolist.append(resp[1:])

        #await ctx.send("API overload")
        print(convolist,"lines:", len(convolist))
        if (len(convolist) >= 17):
            itBot()


@bot.command()
async def s(ctx):

    getstat = requests.get(apidomain + "/st?m=dc")
    response = getstat.text
    await ctx.send("```" + response + "```")

            
@bot.command()
async def r(ctx, arg=''):
    newarg = arg
    if "surf_" in arg:
            newarg = arg.replace("surf_", "420surf420")
            print (newarg)
    recson = requests.get(apidomain + "/lb?arg=" + newarg + "&m=dc")
    response = (str(recson.text))
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
            maplist= requests.get(apidomain + "/gm?m=dc")

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
    getstat = requests.get(apidomain + "/tp?m=dc")
    response = getstat.text
    await ctx.send("```" + "Total time played on server\n\n" + response + "```")
       
 
@bot.command()
async def ch(ctx, *arg):
    videoTitle = ""
    idd = ""
    await ctx.message.delete()
    print (videoTitle)
    print(idd)

    for i in arg:
            if "idv=" in i:
                idd = i.replace("idv=", "")
            else:
                videoTitle = videoTitle + str(i) + " "


    if " " in idd or idd == "":
            idd = "4c8_IcqLLo0"

    if videoTitle == "":
        videoTitle = "Check it"
    changename.changeTitle(videoTitle, idd)
    time.sleep(0)
    await ctx.send("https://www.youtube.com/watch?v=" + idd)
    


    


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
         
