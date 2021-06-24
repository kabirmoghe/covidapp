from flask import Flask, redirect, url_for, render_template, request
import covidapp
import os.path
from os import path
import readbucketdata
import pandas as pd


app = Flask(__name__)
app.secret_key = 'SECRET KEY'

@app.route("/")
def home():

	readbucketdata.readbucketdata('vaxx').to_csv('vaxxdataset.csv')
	readbucketdata.readbucketdata('full').to_csv('fulldataset.csv')

	return render_template("index.html")
	

@app.route("/data", methods = ['POST', 'GET'])
def countyinfo():

	if path.exists('vaxxdataset.csv') == False and path.exists('fulldataset.csv') == False:
		readbucketdata.readbucketdata('vaxx').to_csv('vaxxdataset.csv')
		readbucketdata.readbucketdata('full').to_csv('fulldataset.csv')
	
	if request.method == "POST":
		county = request.form["cty"]
		if county == '':
			return render_template('empty.html')
		else:

			data1, data2 = pd.read_csv('fulldataset.csv'), pd.read_csv('vaxxdataset.csv')

			if county in data1['County Name'].values and county in data2['County Name'].values:

				covidapp.vaxx_plot(county)
				covidapp.avg_plot(county)
				allinfo = covidapp.county_stats(county)
				
				tbl, stat, info, rec, risk_pos, pct, y_n_mask, mask_details, color, risk = allinfo

				ctyrisk_pos = risk_pos - 12.5

				if round(pct) == 100.0:
					ptile = 'Top ~99%'
				else:
					if pct >= 50:
						ptile = 'Top ~{}%'.format(str(round(100.0-pct)))
					else:
						ptile = 'Bottom ~{}%'.format(str(round(pct)))

				if county.split(', ')[1] == 'TX' or county.split(', ')[1] == 'HI':
					note = 'Neither Hawaii nor Texas provide county-level data on vaccinations, hence why the visualization below is empty.'

				else:
					note = 'The visualizations below show the percentage of fully vaccinated people within the county broken down by age group.'

				return render_template("result.html", county = county, tbl = [tbl.to_html(classes='data', header = True)], stat = stat, info = info, rec = rec, risk_pos = risk_pos, pct = pct, ctyrisk_pos = ctyrisk_pos, y_n_mask = y_n_mask, mask_details = mask_details, color = color, note = note, ptile = ptile, risk = risk)
			
			else:
				return render_template("undef_result.html", issue = 'Please enter a valid county name (i.e. Orange County, CA). The county you entered, {}, may not have complete information.'.format(county))
	else:
		ctys = covidapp.county_list()
		return render_template("data.html", ctys = ctys)
		#return render_template("data.html", states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'])
			

@app.route("/stats", methods = ['POST', 'GET'])
def stats():
	if path.exists('vaxxdataset.csv') == False and path.exists('fulldataset.csv') == False:
		readbucketdata.readbucketdata('vaxx').to_csv('vaxxdataset.csv')
		readbucketdata.readbucketdata('full').to_csv('fulldataset.csv')
		
	if request.method == "POST":
		choice = request.form["choice"]
		if choice == 'vaxx':
			date = covidapp.multivaxx_plot()
			return render_template("vaxx_stats.html", date = date)
		else:
			if choice == 'c':
				top10, bot10, date, num0 = covidapp.usplot('c')
				return render_template("cases_stats.html", top10 = [top10.to_html(classes='data', header = True)], bot10 = [bot10.to_html(classes='data', header = True)], choice = choice, date = date, num0 = num0)
				#date = covidapp.multivaxx_plot()
			else:
				top10, bot10, date, num0 = covidapp.usplot('d')
				return render_template("deaths_stats.html", top10 = [top10.to_html(classes='data', header = True)], bot10 = [bot10.to_html(classes='data', header = True)], choice = choice, date = date, num0 = num0)

	else:
		return render_template("statshome.html")

@app.route("/explore", methods = ['POST', 'GET'])
def explore():
	if path.exists('vaxxdataset.csv') == False and path.exists('fulldataset.csv') == False:
		readbucketdata.readbucketdata('vaxx').to_csv('vaxxdataset.csv')
		readbucketdata.readbucketdata('full').to_csv('fulldataset.csv')

	if request.method == "POST":
		# FIX LOAD DATASET
		attr1 = request.form["choice1"]
		attr2 = request.form["choice2"]
		trendline = request.form["trendline"]

		covidapp.scatter(attr1, attr2, trendline)

		return render_template("explore_results.html", attr1 = attr1, attr2 = attr2, trendline = trendline)
			
	else:
		cols = [col for col in pd.read_csv('fulldataset.csv').columns[3:] if col != 'State' and "Mask" not in col]
		cols.reverse()
		return render_template("explorehome.html", cols = cols)

@app.route("/about")
def about():
	return render_template("about.html")

if __name__ == '__main__':
    app.run(debug = True)
