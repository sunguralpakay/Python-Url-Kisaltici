from flask import Flask, render_template, request, redirect, send_from_directory, jsonify
from replit import db
import random, string, json, os, validators, logging, requests
from middleware import middleware

print_db_on_start = False
export_db_on_start = False
import_db_on_start = False

# Kısaltma
url = "https://replit.sh/" # URL adresiniz
img_url = "https://imgrender.replit.sh/"
siteName = "Replit.sh" # sitenizin adı

if print_db_on_start:
	print(list(db.keys()))

if export_db_on_start:
	outdb = {}
	print("Starting DB Export...")
	for x in list(db.keys()):
		print("Set key " + str(x) + " to " + str(db[x]))
		outdb[x] = db[x]
	f = open('out.json', 'w')
	with open('out.json', 'w') as outfile:
		print("File opened...")
		json.dump(outdb, outfile)
		print("File written...")
		print("File closed...")

if import_db_on_start:
	print("Clearning old db")
	for x in list(db.keys()):
		print("Cleared key " + str(x))
		del db[x]
	print("Opening JSON File")
	with open("in.json", "r") as read_file:
		print("Converting JSON encoded data into Python dictionary")
		indb = json.load(read_file)
	print("Starting DB Import...")
	for key, value in indb.items():
		print ("Set key " + str(key) + " to " + str(value))
		db[key] = value
	print("Database imported")

users = json.loads(os.getenv('IDS'))

app = Flask('app')

def newString():
	letters = string.ascii_lowercase
	result_str = ''.join(random.choice(letters) for i in range(8))
	return result_str

def getStrings(id):
	urls = db["user_id_" + id]
	return urls

def compileLine(id): 
	value = db[id]
	key = id[10:]
	return '<tr><td>' + id[10:] + '</td><td>' + db[id] + '</td><td>' + '<a href ="https://replit.sh/delete/' + id[10:] + '">Delete Entry</a></td><td><a href ="https://replit.sh/edit/' + id[10:] + '">Edit Entry</a></td></tr>'

@app.route('/', methods=['GET', 'POST'])
def index():
	if len(request.headers['X-Replit-User-Id']) == 0 or int(request.headers['X-Replit-User-Id']) not in users:
		return render_template('index.html', siteName=siteName)
	try:
		return render_template(
		'submit.html',
		siteName=siteName,
		user_id=request.headers['X-Replit-User-Id'],
		user_name=request.headers['X-Replit-User-Name'],
		error=""
	)
	except:
		return render_template('error.html', code = "401", message = "You aren't an allowed user, sorry!", siteName=siteName)

@app.route('/custom', methods=['GET', 'POST'])
def custom():
	try:
		return render_template(
		'custom.html',
		siteName=siteName,
		user_id=request.headers['X-Replit-User-Id'],
		user_name=request.headers['X-Replit-User-Name'],
		error=""
	)
	except:
		return render_template('error.html', code = "401", siteName=siteName, message = "You aren't an allowed user, sorry!")

@app.route('/social', methods=['GET', 'POST'])
def social():
	try:
		return render_template(
		'social.html',
		siteName=siteName,
		user_id=request.headers['X-Replit-User-Id'],
		user_name=request.headers['X-Replit-User-Name'],
		error=""
	)
	except:
		return render_template('error.html', code = "401", siteName=siteName, message = "You aren't an allowed user, sorry!")

@app.route('/dash', methods=['GET', 'POST'])
def dashboard():
	try:
		ids = getStrings(request.headers['X-Replit-User-Id'])
		idTable = ""
		for id in ids:
			idTable = idTable + compileLine(id)
		return render_template(
			'dashboard.html',
			siteName=siteName,
			user_id=request.headers['X-Replit-User-Id'],
			user_name=request.headers['X-Replit-User-Name'],
			user_roles=request.headers['X-Replit-User-Roles'],
			idTable = idTable,
			error = ""
		)
	except:
		return render_template(
			'dashboard.html',
			siteName=siteName,
			user_id=request.headers['X-Replit-User-Id'],
			user_name=request.headers['X-Replit-User-Name'],
			user_roles=request.headers['X-Replit-User-Roles'],
			idTable = idTable,
			error = "<p>No Entries Yet</p>"
		)

@app.route('/delete/<string:id>', methods=['GET', 'POST'])
def delete(id):
	if not id:
		id = "Please stop trying to break the site lol"
	return render_template(
		'delete.html',
		siteName=siteName,
		user_id=request.headers['X-Replit-User-Id'],
		user_name=request.headers['X-Replit-User-Name'],
		user_roles=request.headers['X-Replit-User-Roles'],
		id = id
	)

@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit(id):
	if not id:
		id = "Please stop trying to break the site lol"
	return render_template(
		'edit.html',
		siteName=siteName,
		user_id=request.headers['X-Replit-User-Id'],
		user_name=request.headers['X-Replit-User-Name'],
		user_roles=request.headers['X-Replit-User-Roles'],
		oldurl = db["short_url_" + id],
		id = id
	)

@app.route('/del', methods=['POST'])
def deleteEntry():
	if len(request.headers['X-Replit-User-Id']) == 0 or int(request.headers['X-Replit-User-Id']) not in users:
		return render_template('error.html', siteName=siteName, code = "401", message = "You aren't allowed to do that!")
	try:
		user_id = request.headers['X-Replit-User-Id']
		id = request.form['id']
		users_ids = db["user_id_" + user_id]
		try:
			users_ids.remove("short_url_" + id)
			del db["short_url_" + id]
			db["user_id_" + user_id] = users_ids
			return redirect(url + "dash", 302)
		except:
			return render_template('error.html', code = "401", siteName=siteName, message = "You aren't allowed to do that!")
	except:
		return render_template('error.html', code = "401", siteName=siteName, message = "You aren't allowed to do that!")

@app.route('/edt', methods=['POST'])
def editEntry():
	if len(request.headers['X-Replit-User-Id']) == 0 or int(request.headers['X-Replit-User-Id']) not in users:
		return render_template('error.html', siteName=siteName, code = "401", message = "You aren't allowed to do that!")
	try:
		user_id = request.headers['X-Replit-User-Id']
		id = request.form['id']
		newurl = request.form['newurl']
		try:
			db["short_url_" + id] = newurl
			return redirect(url + "dash", 302)
		except:
			return render_template('error.html', code = "401", siteName=siteName, message = "You aren't allowed to do that!")
	except:
		return render_template('error.html', code = "401", siteName=siteName, message = "You aren't allowed to do that!")

@app.route('/favicon.ico', methods=['GET', 'POST'])
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route('/socialpost.png', methods=['GET', 'POST'])
def socialpostimg():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'socialpost.png')

@app.route('/wp-login.php', methods=['GET', 'POST'])
def wploginphp():
	flask.abort(404)

@app.route('/sitemap.xml', methods=['GET', 'POST'])
def sitemap():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')

@app.route('/googlecec87f30263d281f.html', methods=['GET', 'POST'])
def googleverifbsorwhatever():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'googlecec87f30263d281f.html')

@app.route('/robots.txt', methods=['GET', 'POST'])
def robots():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt')

@app.route('/humans.txt', methods=['GET', 'POST'])
def humans():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'humans.txt')

@app.route('/getid', methods=['GET', 'POST'])
def getId():
	return render_template(
		'getid.html',
		siteName=siteName,
		user_id=request.headers['X-Replit-User-Id'],
		user_name=request.headers['X-Replit-User-Name'],
		user_roles=request.headers['X-Replit-User-Roles']
	)

@app.route('/<string:key>', methods=['GET', 'POST'])
def sendUrl(key):
	print(request.headers['User-Agent'])
	if request.headers.get('User-Agent') == 'Mozilla/5.0 (compatible; PaperLiBot/2.1; https://support.paper.li/entries/20023257-what-is-paper-li)' or request.headers.get('User-Agent') == 'Twitterbot/1.0' or request.headers.get('User-Agent') == "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)":
		print("its a bot")
		socialObject = db['social_media_' + key]
		repl_title = socialObject['title']
		repl_author = socialObject['username']

		print(f'{repl_title} - Replit')
		print(f'{repl_title} is a repl by {repl_author}.')
		print(f'{img_url}{key}.png')

		return render_template(
		'socialpost.html',
		siteName=siteName,
		url=url + key,
		twitter_title=f'{repl_title} - Replit',
		twitter_desc=f'{repl_title} is a repl by {repl_author}.',
		image_url=f'{img_url}{key}.png'
	)
	keyFinal = "short_url_" + key
	if not db[keyFinal]:
		return render_template('error.html', code = "404", siteName=siteName, message = "That URL could not be found!")
	else:
		redirectUrl = db[keyFinal]
		try:
			social = db[f'social_media_{key}']
			if social['talk'] == "":
				return redirect(redirectUrl, 302)
			else:
				return redirect(social['talk'], 302)
		except:
			return redirect(redirectUrl, 302)

@app.route('/metadata/<string:key>', methods=['GET', 'POST'])
def sendMeta(key):
	data = db[f'social_media_{key}']
	url = db[f'short_url_{key}']
	try:
		return jsonify({'url': url, 'title': data['title'], 'username': data['username'], 'talk': data['talk'], 'code': data['code']})
	except:
		return jsonify({'url': url, 'title': data['title'], 'username': data['username'], 'talk': data['talk']})
	
@app.route('/new', methods=['GET', 'POST'])
def newEntry():
	if len(request.headers['X-Replit-User-Id']) == 0 or int(request.headers['X-Replit-User-Id']) not in users:
		return render_template('error.html', siteName=siteName, code = "401", message = "You aren't allowed to do that!")
	key = "short_url_" + newString()
	keys = list(db.keys())
	while key in keys:
		key = "short_url_" + newString()
		keys = list(db.keys())
	if not validators.url(str(request.form['url'])):
		return render_template(
			'submit.html',
			siteName=siteName,
			user_id=request.headers['X-Replit-User-Id'],
			user_name=request.headers['X-Replit-User-Name'],
			error="That was not a valid URL. Please enter a valid URL and try again."
		)
	db[key] = request.form['url']
	try:
		strings = list(getStrings(request.headers['X-Replit-User-Id']))
	except:
		strings = []
	strings.append(key)
	db["user_id_" + request.headers['X-Replit-User-Id']] = strings
	return render_template('done.html', siteName=siteName, newUrl = url + key[10:])

@app.route('/newcustom', methods=['GET', 'POST'])
def newCustom():
	if len(request.headers['X-Replit-User-Id']) == 0 or int(request.headers['X-Replit-User-Id']) not in users:
		return render_template('error.html', siteName=siteName, code = "401", message = "You aren't allowed to do that!")
	try:
		key = "short_url_" + request.form['id']
		keys = list(db.keys())
		if key in keys:
			return render_template('error.html', siteName=siteName, code = "401", message = "That ID Already Exists!")
		if not validators.url(str(request.form['url'])):
			return render_template(
				'manual.html',
				siteName=siteName,
				user_id=request.headers['X-Replit-User-Id'],
				user_name=request.headers['X-Replit-User-Name'],
				error="That was not a valid URL. Please enter a valid URL and try again."
			)
		db[key] = request.form['url']
		try:
			strings = list(getStrings(request.headers['X-Replit-User-Id']))
		except:
			strings = []
		strings.append(key)
		db["user_id_" + request.headers['X-Replit-User-Id']] = strings
		return render_template('done.html', siteName=siteName, newUrl = url + key[10:])
	except:
		return render_template('error.html', siteName=siteName, code = "401", message = "You aren't allowed to do that!")

@app.route('/newsocial', methods=['GET', 'POST'])
def newSocial():
	if len(request.headers['X-Replit-User-Id']) == 0 or int(request.headers['X-Replit-User-Id']) not in users:
		return render_template('error.html', siteName=siteName, code = "401", message = "You aren't allowed to do that!")
	urlSubmitted = request.form['url']
	urlTalk = request.form['talk']
	code = request.form['code']
	key = newString()
	keyFinished = "short_url_" + key 
	keys = list(db.keys())
	while keyFinished in keys:
		key = newString()
		keyFinished = "short_url_" + key 
		keys = list(db.keys())
	if not validators.url(str(request.form['url'])):
		return render_template(
			'social.html',
			siteName=siteName,
			user_id=request.headers['X-Replit-User-Id'],
			user_name=request.headers['X-Replit-User-Name'],
			error="That was not a valid URL. Please enter a valid URL and try again."
		)
	try:	
		db[keyFinished] = urlSubmitted
		indexOfAt = urlSubmitted.index("@")
		indexOfSlash = urlSubmitted.index("/", indexOfAt)
		x = list(urlSubmitted[indexOfSlash + 1:].title())
		for (i, s) in enumerate(list(urlSubmitted[indexOfSlash + 1:])):
			if s.isupper():
				x[i] = s
		title = "".join(x).replace("-", " ").replace("_", " ")
		x = list(urlSubmitted[indexOfAt + 1:indexOfSlash].title())
		for (i, s) in enumerate(list(urlSubmitted[indexOfAt + 1:indexOfSlash])):
			if s.isupper():
				x[i] = s
		username = "".join(x)
		socialMeta = {"title": title, "username": username, "talk": urlTalk, "code": code}
		db['social_media_' + key] = socialMeta
	except Exception as e:
			print("secondfailed")
			print(e)
			return render_template('error.html', siteName=siteName, code = "401", message = "Not a valid Replit URL!")

	try:
		strings = list(getStrings(request.headers['X-Replit-User-Id']))
	except:
		strings = []
	strings.append(keyFinished)
	db["user_id_" + request.headers['X-Replit-User-Id']] = strings
	requests.get(f'{img_url}/{key}')
	return render_template('done.html', siteName=siteName, newUrl = url + keyFinished[10:])

@app.errorhandler(400)
def error_bad_request(e):
	return render_template('error.html', siteName=siteName, code = "400", message = "Bad Request")

@app.errorhandler(401)
def error_unauthorized(e):
	return render_template('error.html', siteName=siteName, code = "401", message = "Unauthorized")

@app.errorhandler(403)
def error_forbidden(e):
	return render_template('error.html', siteName=siteName, code = "403", message = "Forbidden")

@app.errorhandler(404)
def error_page_not_found(e):
	return render_template('error.html', siteName=siteName, code = "404", message = "Page not Found")

@app.errorhandler(409)
def error_conflict(e):
	return render_template('error.html', siteName=siteName, code = "409", message = "Conflict")

@app.errorhandler(501)
def error_internal_server_error(e):
	return render_template('error.html', siteName=siteName, code = "500", message = "Internal Server Error")

@app.errorhandler(501)
def error_not_implemented(e):
	return render_template('error.html', siteName=siteName, code = "501", message = "Not Implemented")

@app.errorhandler(502)
def error_bad_gateway(e):
	return render_template('error.html', siteName=siteName, code = "502", message = "Bad Gateway")

app.run(host='0.0.0.0', port=8080)
