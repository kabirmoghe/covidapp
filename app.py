from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta
import covidapp

app = Flask(__name__)
app.secret_key = 'hello'

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/countyinfo", methods = ['POST', 'GET'])
def countyinfo():
	if request.method == "POST":
		county = request.form["cty"]
		stat = covidapp.county_stats(county)
	
		return f"<p>{stat}</p>"
	else:
		return render_template("data.html")

if __name__ == '__main__':
    app.run(debug = True)
