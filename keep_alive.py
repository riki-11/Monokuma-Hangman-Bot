# Code to keep our bot constantly running by pinging it every 5 minutes
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    # this is how our server will be pinged
    return "Hello. I am alive!"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()