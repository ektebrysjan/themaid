from flask import Flask, render_template, request, redirect, url_for, jsonify
import surfsql
import os
import time
import json
import changename as changename
from flask_cors import CORS



# Get config
f = open("config.json", "r")
config = f.read()
config = json.loads(config)

# For loop setter hver key som en varibel med value .
for setting, v in config.items():
    globals()[setting] = str(v)

adomain = domain + 'https://'

todoList = {1: {'instruks': '', 'type': ''}}
iid = 1
nameVar = ""

app = Flask(__name__)
CORS(app)

def pad(word, len_=30, spacer=' '):
    return word + (len_ - len(word)) * spacer

def maketable(arg): 
    table = arg
    qmode = table['qmode']
    tablestr = ""

    if qmode == "all":
        altitle = """__All server records by map:__"""
        title = pad("Map") + pad("Player") + pad("Time")

        for key in (table.keys()):
        	if key == 'qmode':
        		break
        	row = pad(str(table[key]['mapname'])) + pad(str(table[key]['name'])) + pad(str(table[key]['time']))
        	tablestr = (tablestr + row + "\n")
    
    elif qmode == "usr":
        altitle = ""

        try:
        	timespent = table[0]['timeplayed']
        except:
            timespent = "No data"

        altitle = altitle + """__**""" + str(table[0]['name']) + """'s** map times:__\n\nTotal time spent on server: """ + str(timespent)
        title = pad("Map") + pad("Time")
        for x in table.keys():
        	if x == 'qmode':
        		break
        	row = pad(str(table[x]['mapname'])) + pad(str(table[x]['time']))
        	tablestr = (tablestr + row + "\n")
    
    elif qmode == "map":
        altitle = """__Best times on: **""" + str(table[0]['mapname']) + """**:__"""
        title = pad("Place") + pad("Player") + pad("Time")
        for x in table.keys():
            if x == 'qmode':
                   break
            player = str(table[x]['name'])                                               # Hent navn for denne loopen x
            player = (player[:18] + '...') if len(player) > 18 else player          # Er navnet lenger enn 18, forkort
            
            row = pad(("# " + str(x+1))) + pad(player) + pad(str(table[x]['time']))
            tablestr = (tablestr + row + "\n")
           
    return (altitle + "\n\n" + "```apache\n" + title + "\n \n" + tablestr + "```")


@app.route('/')
def index():
    return "no request"


@app.route('/ch', methods=['GET'])
def ytchange():
	YTid = "4c8_IcqLLo0"
	nameR = ""
	if 'id' in request.args:
   		YTid = request.args['id']

	nameR = request.args['n']

	print(nameR)
	#YTid = request.args['id']
	print (YTid)

	newname = changename.changeTitle(nameR, YTid)
	time.sleep(2)
	return redirect("https://www.youtube.com/watch?v=" + YTid, code=302)


@app.route('/st', methods=['GET']) # status
def status():

		os.system('sh sendmsg.sh status')
		f = open('tmuxout.log')
		response = f.read()
		if len(response) > 1000:
				response = response[-1000]
		f.close()
		os.system('chmod 777 tmuxout.log')

		if 'm' in request.args:
			m = request.args['m']
			if m == "html":
				response = "<br />".join(response.split("\n"))
				response = "<pre>" + response + "</pre>"
				return render_template('index.html', data = response)

			elif m == "json":
				jsonres = {}
				jsonres['data'] = response
				jsonres['text'] = response
				return jsonres
			elif m == "dc":
				return response
		return "no format specified."

@app.route('/lb', methods=['GET']) # leaderboards
def leader():
	try:
		if 'arg' in request.args:
			
			arg = request.args['arg']
			
			newarg = arg
			if "420surf420" in arg:
				newarg = arg.replace("420surf420","surf_")
				print(newarg)

			recdict = surfsql.getrecords(newarg)

			response =  maketable(recdict)
		else:
			recdict = surfsql.getrecords()

			response =  maketable(recdict)

	except:
		response = "Invalid command or no data"

	if 'm' in request.args:
			m = request.args['m']
			if m == "html":
				response = "<br />".join(response.split("\n"))
				response = "<pre>" + response + "</pre>"
				return render_template('index.html', data = response)
			elif m == 'json':
				return jsonify(recdict)
			elif m == "dc":
				return response
	return "no format specified."

@app.route('/tp', methods=['GET']) # timeplayed
def timeplayed():

	response = ""
	newline = "\n"
	m = ""
	title = pad("Name") + pad("Time (DD:HH:MM:SS)") + "\n\n"
	if 'm' in request.args:
			m = request.args['m']
			if m == "html":
				newline = "<br>"
				response = title
	else:
		response = title

	timedict = surfsql.timetopten()
	for x in timedict.keys():
		name = str(timedict[x]['name'])
		time = str(timedict[x]['time'])
		response = response + pad(name) + pad(time) + newline

	if m == "html":
		response = "<pre>" + response + "</pre>"
		return render_template('index.html', data = response)

	elif m == "json":
		return jsonify(timedict)
	elif m == "dc":
		return response
	return "no format specified."


@app.route('/gm', methods=['GET']) # timeplayed
def getmaps():
	mapmesg = ""
	maplist = surfsql.getmaps()
	response = ""
	
	if 'm' in request.args:
			m = request.args['m']
			if m == "html":
				for map in maplist:
					mapmesg = mapmesg + str(map) + "<br>"
				response = mapmesg
				response = "<pre>" + response + "</pre>"
				return render_template('index.html', data = response)
			
			elif m == "json":
				return jsonify(maplist)

			elif m == "dc":
				for map in maplist:
					mapmesg = mapmesg + str(map) + "\n"
				return mapmesg

	return "no format specified. " + m

@app.route('/stock', methods=['GET'])
def openstock():
	return render_template('stock.html')	


@app.route("/todo", methods=['GET'])
def rettern():
	global todoList


	return jsonify(todoList)
    
@app.route("/addtodo", methods=['GET'])
def addtodo():
	global iid
	
	iid+=1
	text_field = request.args.get('text-field')
	todoList[iid] = {'instruks': text_field, 'type': "cmd"}

	return jsonify(todoList)

@app.route("/remote", methods=['GET'])
def form():
    html = """
    <style>
    body {
    background: black;
    color: white;
    }
    </style>
    <form action="/addtodo" method="GET">
      <label>Text field:</label>
      <input type="text" id="text-field" name="text-field">
      <br>
      <button type="submit">Submit</button>
    </form>
    """
    return html

if __name__ == "__main__":
    app.run(host=domain, port=aport, ssl_context=('/etc/letsencrypt/live/ma-surf.no/fullchain.pem', '/etc/letsencrypt/live/ma-surf.no/privkey.pem'))
