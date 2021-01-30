from flask import Flask, render_template, request, redirect, url_for
import surfsql
import os
import json
from flask_cors import CORS

# Get config
f = open("config.json", "r")
config = f.read()
config = json.loads(config)

# For loop setter hver key som en varibel med value .
for setting, v in config.items():
    globals()[setting] = str(v)

adomain = domain + 'https://'

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "no request"

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
			if m == "www":
				response = "<br />".join(response.split("\n"))
				response = "<pre>" + response + "</pre>"
				return render_template('index.html', data = response)

		return response

@app.route('/lb', methods=['GET']) # leaderboards
def leader():
	try:
		if 'arg' in request.args:
			leaderboard = request.args.get('arg')
			response =  surfsql.maketable(leaderboard)
		else:
			response = surfsql.maketable("")
	except:
		response = "Invalid command or no data"

	if 'm' in request.args:
			m = request.args['m']
			if m == "www":
				response = "<br />".join(response.split("\n"))
				response = "<pre>" + response + "</pre>"
				return render_template('index.html', data = response)

	return response

@app.route('/tp', methods=['GET']) # timeplayed
def timeplayed():

	response = ""
	newline = "\n"
	m = ""
	title = surfsql.pad("Name") + surfsql.pad("Time (DD:HH:MM:SS)") + "\n\n"
	if 'm' in request.args:
			m = request.args['m']
			if m == "www":
				newline = "<br>"
				response = title
	else:
		response = title

	timedict = surfsql.timetopten()
	for item in timedict:
		name = str(item[0])
		time = str(surfsql.gettime(item[2], 0))
		response = response + surfsql.pad(name) + surfsql.pad(time) + newline

	if m == "www":
		response = "<pre>" + response + "</pre>"
		return render_template('index.html', data = response)
	return response

@app.route('/gm', methods=['GET']) # timeplayed
def getmaps():
	mapmesg = ""
	maplist = (surfsql.getmaps())
	
	if 'm' in request.args:
			m = request.args['m']
			if m == "www":
				for map in maplist:
					mapmesg = mapmesg + str(map) + "<br>"
			response = mapmesg
			response = "<pre>" + response + "</pre>"
			return render_template('index.html', data = response)
			
	else:
		response = json.dumps(maplist)

	return response

if __name__ == "__main__":
    app.run(host=domain, port=aport, ssl_context=('/home/steam/ssl/fullchain.pem', '/home/steam/ssl/privkey.pem'))