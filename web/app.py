"""
# working Code for web app
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, logging
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
#api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]

def verify_user(username):
    if users.find({"Username" : username}).count() != 0:
        return True
    else:
        return False

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #GET form fields
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        verifyUser = verify_user(username)

        if verifyUser:
            retJson = {
                "Message" : "This user is allready registered",
                "status" : 301
            }
            return jsonify(retJson)

        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Sentence": "",
            "Tokens"  : 6
        })
        retmap = {
            "status" : 200,
            "msg": "You successfully signed up for the api"
        }
        return jsonify(retmap)
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0')

"""


from flask import Flask, jsonify,make_response, request, render_template, redirect, url_for, session, logging
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
#api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]

def verify_user(username):
    if users.find({"Username" : username}).count() != 0:
        return True
    else:
        return False

def verify_pw(username, password):
    hashed_pw = users.find({
        "Username" : username
        })[0]["Password"]

    if bcrypt.hashpw(password.encode("utf8"), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({
        "Username" : username
        })[0]["Tokens"]

    return tokens


@app.route("/papa")
def getcookie():
    msg = request.cookies.get("result")
    return "<h1> You are signed up successfully :"+msg+" </h1>"

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/store", methods=["GET", "POST"])
def store():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        sentence = request.form["sentence"]

        verifyUser = verify_user(username)
        if verifyUser == False:
            retJson = {
                "Message" : "This user doesn't exist in the database",
                "status" : 301
            }
            return jsonify(retJson)

        correct_pw = verify_pw(username, password)

        if not correct_pw:
            retJson = {
                "message": "Incorrect password",
                "status" : 302
            }
            return jsonify(retJson)

        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "Message" : "please purchase more tokens",
                "status" : 303
            }
            return jsonify(retJson)

        # step 5: store the sentence and return 200 and take one token away
        users.update({
            "Username" : username
        },{
            "$set":{
            "Sentence": sentence,
            "Tokens": num_tokens-1
            }
        })
        retJson = {
            "status" : 200,
            "msg" : "Your message was saved succesfully"
        }
        return jsonify(retJson)
    return render_template("store.html")


@app.route("/check", methods=["GET", "POST"])
def check():
    if request.method == "POST":
        #GET form fields
        username = request.form["username"]
        password = request.form["password"]

        verifyUser = verify_user(username)
        if verifyUser == False:
            retJson = {
                "Message" : "This user doesn't exist in the database",
                "status" : 301
            }
            return jsonify(retJson)

        correct_pw = verify_pw(username, password)

        if not correct_pw:
            retJson = {
                "status": 302,
                "msg" : "wrong password"
            }
            return jsonify(retJson)
        # step 4 verify user has enough token
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status" : 301,
                "msg" : "Sorry you are out of tokens please buy more"
            }
            return jsonify(retJson)

        # make the user pay
        users.update({
            "Username": username
        }, {"$set": {"Tokens": num_tokens-1}})

        # step 5 store the sentence, take one away and return 200
        sentence = users.find({
            "Username": username
        })[0]["Sentence"]

        retJson = {
            "status" : 200,
            "Msg" : sentence
        }
        return jsonify(retJson)
    return render_template("check.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #GET form fields
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        verifyUser = verify_user(username)

        if verifyUser:
            retJson = {
                "Message" : "This user is allready registered",
                "status" : 301
            }
            return jsonify(retJson)

        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Sentence": "",
            "Tokens"  : 6
        })
        retmap = {
            "status" : 200,
            "msg": "You successfully signed up for the api"
        }
        rett = username

    resp = make_response(render_template("new1.html"))
    resp.set_cookie("result", rett)
    return resp

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0')
