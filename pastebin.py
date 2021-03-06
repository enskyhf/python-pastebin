from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, Response
from random import sample
from string import ascii_letters, digits
import logging
import sqlite3
logging.basicConfig(filename='paste.log',level=logging.DEBUG)
app = Flask(__name__, static_url_path='')

def app_start(host,port):
    app.run(host=host, port=port)

DATABASE = 'paste.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(query,args=()):
    cur = get_db().execute(query, args)
    get_db().commit()
    cur.close()

def make_id():
	return  "".join(sample((ascii_letters) * 10, 10))

def make_password():
    s = ascii_letters + digits + "!@*^$()[]+,.:~-_"
    passlen = 15
    return "".join(sample(s,passlen ))

def insert_paste(idx,contentx,passwordx):
    insert_db("INSERT INTO pastes (id, content, password) VALUES(?, ?, ?)",[idx, contentx, passwordx])
    
def get_paste(idx):
    data = query_db("Select content from pastes where id=?",[idx],True)
    if data:
        return data[0]
    else:
        return "Invaild ID!"
    
def delete_paste(idx,password):
    data = query_db("Select password from pastes where id=?",[idx],True)
    if data and data[0] == password:
        insert_db("DELETE FROM pastes WHERE id = ?",[idx])
        return "Paste deleted!"
    else: 
        if not data:
            return "Invalid paste ID."
    if data[0] != password:
        return "Invalid password."

@app.route("/")
def show_form():
    return app.send_static_file('index.html') 
    
@app.route("/process/", methods=["POST"])
def create_paste():
    fname = make_id()
    password = make_password()
    text = request.form.get("text")
    insert_paste(fname,text,password)
    logging.info(fname)
    return render_template('process.html', fname=fname, password=password)

@app.route("/p/<slug>/")
def show_paste(slug):
    contents = get_paste(slug)
    return render_template('paste.html', pasteContent=contents,)

@app.route("/p/<slug>/raw")
def show_raw_paste(slug):
    contents = get_paste(slug)
    return Response(contents, mimetype='text/plain')

@app.route("/p/<slug>/delete/<slug2>")
def remove_paste(slug,slug2):
    result = delete_paste(slug,slug2)
    return result




app_start('0.0.0.0',6060)
