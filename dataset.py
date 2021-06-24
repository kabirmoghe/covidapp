import pandas as pd
import requests
from bs4 import BeautifulSoup
import io
from io import StringIO
import os
import boto3
import readbucketdata


# Creates COVID-19 County Level Dataset

# Basic Stats Relating to the Virus *download "stat_data.csv", attached, and insert the path of the file*

# "stat_data.csv" comes from the census website and has been cut down to only a few important attributes; download the full file here: https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/cc-est2019-alldata.csv

def create_race_data():
    
    stat_data = pd.read_csv('https://raw.githubusercontent.com/kabirmoghe/Demographic-Data/main/stat_data.csv', index_col = 0)
    
    pop_url = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_county_population_usafacts.csv'

    pop = pd.read_csv(pop_url)
    pop['countyFIPS'] = pop['countyFIPS'].apply(lambda value: '0' + str(value) if len(str(value)) == 4 else str(value))
    pop = pop[pop['County Name'] != 'Statewide Unallocated'].reset_index(drop = True)[['County Name', 'State','population']].rename(columns = {'population':'Population'})
    pop['County Name'] = pop['County Name']  + ', ' + pop['State']
    
    race_data = pd.merge(pop, stat_data)
    
    race_cols = ['African American', 'Hispanic', 'Asian American', 'White American', 'Native American or Alaska Native', 'Native Hawaiian or Pacific Islander']

    for col in race_cols:
        race_data['% ' + str(col)] = round(race_data[col + ' Population'] / race_data['Population'] * 100,2)
        race_data = race_data.drop(col + ' Population', axis = 1)    
    
    race_data = race_data.drop(['Population','State'], axis = 1)
    
    race_data['Approximate Population Density'] = round(race_data['Approximate Population Density'], 2)
    
    return race_data

# Income / Unemployment Data

def create_inc_unemp_data():
    
    income_data = pd.read_excel('https://www.ers.usda.gov/webdocs/DataFiles/48747/Unemployment.xls?v=2512', skiprows = 4)[['area_name','Unemployment_rate_2019', 'Median_Household_Income_2019']].reset_index(drop = True).rename(columns = {'area_name': 'County Name', 'Unemployment_rate_2019': '% Unemployed', 'Median_Household_Income_2019':'Median Household Income'})
    
    income_data['% Unemployed'] = income_data['% Unemployed'].round(2)
    
    ### Broken down below
    
    # income_data = pd.read_excel('https://www.ers.usda.gov/webdocs/DataFiles/48747/Unemployment.xls?v=2512', skiprows = 7)
    
    #income_data = income_data[['area_name','Unemployment_rate_2019', 'Median_Household_Income_2018']] # Includes the unemployment rate in 2019 and the median household income as of 2018 (per county)

    #income_data = income_data.reset_index(drop = True)

    #income_data = income_data.rename(columns = {'area_name': 'County Name', 'Unemployment_rate_2019': '% Unemployed', 'Median_Household_Income_2018':'Median Household Income'})
    
    return income_data

# Education Data

def create_edu_data():
    sts = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado",
           "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois",
           "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland",
           "Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
           "Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York",
           "North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
           "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah",
           "Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming","Puerto Rico"]
    
    edu_link = 'https://www.ers.usda.gov/webdocs/DataFiles/48747/Education.xls?v=6188.1'
    
    edu_data = pd.read_excel(edu_link).drop([0,1,2,4])
    
    edu_data.columns = edu_data.loc[3].values
    
    edu_data = edu_data.drop(3).reset_index(drop = True)

    for value in edu_data['Area name']:
        if value in sts:
            edu_data.drop(edu_data[edu_data['Area name'] == value].index[0], inplace = True)
        
    edu_data['Area name'] = edu_data['Area name'] + ', ' + edu_data['State']

    edu_data = edu_data.rename(columns = {'Area name': 'County Name'})

    edu_data = edu_data[['County Name', "Percent of adults completing some college or associate's degree, 2015-19"]]
    
    edu_data['Percent of adults completing some college or associate\'s degree, 2015-19'] = edu_data['Percent of adults completing some college or associate\'s degree, 2015-19'].apply(lambda value: round(value, 1))
    
    #pop data
    
    pop_url = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_county_population_usafacts.csv'

    pop = pd.read_csv(pop_url)
    pop['countyFIPS'] = pop['countyFIPS'].apply(lambda value: '0' + str(value) if len(str(value)) == 4 else str(value))
    pop = pop[pop['County Name'] != 'Statewide Unallocated'].reset_index(drop = True)[['County Name', 'State','population']].rename(columns = {'population':'Population'})
    pop['County Name'] = pop['County Name']  + ', ' + pop['State']
    
    edu_data = pd.merge(pop, edu_data, on = 'County Name')
    
    edu_data.drop(['State', 'Population'], axis = 1, inplace = True)
    
    edu_data.rename(columns = {'Percent of adults completing some college or associate\'s degree, 2015-19': '% Adults With Degree 2015-19'}, inplace = True)

    return edu_data

# Creates a dataframe of statewide data about mask reqs

def create_mask_data():
    states = {
        'District of Columbia': 'DC',
        'Puerto Rico': 'PR',
        'Alabama': 'AL',
        'Montana': 'MT',
        'Alaska': 'AK',
        'Nebraska': 'NE',
        'Arizona': 'AZ',
        'Nevada': 'NV',
        'Arkansas': 'AR',
        'New Hampshire': 'NH',
        'California': 'CA',
        'New Jersey': 'NJ',
        'Colorado': 'CO',
        'New Mexico': 'NM',
        'Connecticut': 'CT',
        'New York': 'NY',
        'Delaware': 'DE',
        'North Carolina': 'NC',
        'Florida': 'FL',
        'North Dakota': 'ND',
        'Georgia': 'GA',
        'Ohio': 'OH',
        'Hawaii': 'HI',
        'Oklahoma': 'OK',
        'Idaho': 'ID',
        'Oregon': 'OR',
        'Illinois': 'IL',
        'Pennsylvania': 'PA',
        'Indiana': 'IN',
        'Rhode Island': 'RI',
        'Iowa': 'IA',
        'South Carolina': 'SC',
        'Kansas': 'KS',
        'South Dakota': 'SD',
        'Kentucky': 'KY',
        'Tennessee': 'TN',
        'Louisiana': 'LA',
        'Texas': 'TX',
        'Maine': 'ME',
        'Utah': 'UT',
        'Maryland': 'MD',
        'Vermont': 'VT',
        'Massachusetts': 'MA',
        'Virginia': 'VA',
        'Michigan': 'MI',
        'Washington': 'WA',
        'Minnesota': 'MN',
        'West Virginia': 'WV',
        'Mississippi': 'MS',
        'Wisconsin': 'WI',
        'Missouri': 'MO',
        'Wyoming': 'WY',
    }
    
    mainContent = requests.get("https://www.aarp.org/health/healthy-living/info-2020/states-mask-mandates-coronavirus.html")

    mask_html = BeautifulSoup(mainContent.text,'lxml')
    
    ps = []

    for paragraph in mask_html.find_all('p'):
        ps.append(paragraph.text.strip())
    
    mandates = [val for val in ps if val.split(':')[0] == 'Statewide order' or val.split(':')[0] == 'Citywide order'or val.split(':')[0] == 'Territory-wide order']
    
    sps = []

    for span in mask_html.find_all('span'):
    
        txt = span.text.strip()
    
        if txt != '' and txt != '|':
            sps.append(txt)

    date_txt = sps[15].split()
        
    date_updated = date_txt[5] + ' ' + date_txt[6] + ' ' + date_txt[7]
    
    def clean_mandates(ls):
    
        clean_mandates = []
    
        for string in mandates:
        
            s_str = string.split()
        
            if len(s_str) == 3:
                new_str = '{}'.format(s_str[2])
                clean_mandates.append(new_str)
        
            else:
                new_str = '{} ({} {})'.format(s_str[2][:3], s_str[4].title(), s_str[5].title())
                clean_mandates.append(new_str)
            
        return clean_mandates

    cm = clean_mandates(mandates)
    
    state_list = []

    for heading in mask_html.find_all('h4'):
        if len(state_list) == 52:
            break
        else:
            state_list.append(heading.text.strip())
    
    st = pd.DataFrame(state_list, columns=['State'])
    st['State'] = st['State'].map(states)

    md = pd.DataFrame(cm, columns = ['Statewide Mask Mandate (Updated {})'.format(date_updated)])
    
    loc = 0

    for i in range(len(ps)):
        if 'Here’s where each state stands on the use of face masks' in ps[i].split(','):
            loc = i+2
        
    newps = ps[loc:]

    mask_info = pd.DataFrame([val for val in newps if len(val) >150 and 'you' not in val.lower()], columns = ['Mask Mandate Details'])
            
    mask_data = pd.concat([st,md, mask_info], axis = 1)
    
    return mask_data

# Data from usafacts.org (https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/)
# URLs for cases, deaths, and population data from the above website

def create_covid_pop_data():

    no_mo = {1:'January',
                2:'February',
                 3:'March',
                 4:'April',
                 5:'May',
                 6:'June',
                 7:'July',
                 8:'August',
                 9:'September',
                 10:'October',
                 11:'November',
                 12:'December'
                }
    
    cases_url = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv'
    deaths_url = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_deaths_usafacts.csv'
    pop_url = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_county_population_usafacts.csv'
    
    # Removes space in county names
    
    def county_cleaner(cty):
        if cty.split(',')[0][-1] == ' ':
            cty = '{County},{Abbr}'.format(County = cty.split(' ,')[0], Abbr = cty.split(' ,')[1])
        return cty
    
    # Creates the cumulative cases dataframe
    cases = pd.read_csv(cases_url)
    cases['countyFIPS'] = cases['countyFIPS'].apply(lambda value: '0' + str(value) if len(str(value)) == 4 else str(value))
    cases = cases[cases['County Name'] != 'Statewide Unallocated'].reset_index(drop = True)
    cases['County Name'] = cases['County Name']  + ', ' + cases['State']
    cases['County Name'] = cases['County Name'].apply(county_cleaner)
    
    
    # Gets county names
    
    ctynames = cases['County Name']
    
    # Creates the cumulative deaths dataframe
    deaths = pd.read_csv(deaths_url)
    deaths['countyFIPS'] = deaths['countyFIPS'].apply(lambda value: '0' + str(value) if len(str(value)) == 4 else str(value))
    deaths = deaths[deaths['County Name'] != 'Statewide Unallocated'].reset_index(drop = True)
    deaths['County Name'] = deaths['County Name']  + ', ' + deaths['State']
    deaths['County Name'] = deaths['County Name'].apply(county_cleaner)

    def str_int(val):
        if type(val) == str:
            return int(val)
        else:
            return val

    # Creates the population dataframe
    
    pop = pd.read_csv(pop_url)
    pop['countyFIPS'] = pop['countyFIPS'].apply(lambda value: '0' + str(value) if len(str(value)) == 4 else str(value))
    pop = pop[pop['County Name'] != 'Statewide Unallocated'].reset_index(drop = True)
    pop['County Name'] = pop['County Name']  + ', ' + pop['State']
    pop = pd.DataFrame(pop).rename(columns = {'population':'Population'})
    pop['County Name'] = pop['County Name'].apply(county_cleaner)

    def week_compiler(df, c_or_d):
        
        week = pd.concat([df[df.columns[:3]], df[df.columns[-8:]]], axis = 1)

        rawdate = df.columns[-1] 
        year, month, day = [int(value) for value in rawdate.split('-')]
        
        date = '{month} {day}, {year}'.format(month = no_mo[month], day = day, year = year)
        
        cols = df[df.columns[-36:]].columns
        
        g_dates = []

        for i in range(1,len(cols)):
            if i == 1:
                g_dates.append(i)
            else:
                if (i-1)%7 == 0:
                    g_dates.append(i)
                            
        for g_date in g_dates:
            f_date, p_date = g_date+6, g_date-1
            week['{}, Week of {}'.format(c_or_d, cols[g_date])] = df[cols[f_date]] - df[cols[p_date]]
            week['{}, Week of {}'.format(c_or_d, cols[g_date])] = week['{}, Week of {}'.format(c_or_d, cols[g_date])].apply(lambda value: 0 if value < 0 else value)
        
        week['Weekly New {c_or_d} as of {date}'.format(c_or_d = c_or_d, date = date)] = week[week.columns[-6]] - week[week.columns[-13]]
        week.drop(week.columns[3:11], axis = 1, inplace = True)
        week.drop(['countyFIPS', 'State'], axis = 1, inplace = True)
        week = pd.merge(pop, week, on = 'County Name')
        
        case_cols = [col for col in week.columns if c_or_d in col and 'Weekly' not in col]
        
        for col in case_cols:
            raw_date = col.split()[-1]
            year, month, day = raw_date.split('-')
            c_date = '{} {}, {}'.format(no_mo[int(month)], int(day), year)
            
            week['{} Moving Avg. {}'.format(c_or_d, c_date)] = round((((week[col]/7)/week['Population'])*100000),2)
            
            week.drop(col, axis = 1, inplace = True)
        
        week['7-Day Daily {c_or_d} per 100,000 as of {date}'.format(c_or_d = c_or_d, date = date)] = round(((week['Weekly New {c_or_d} as of {date}'.format(c_or_d = c_or_d, date = date)]/7)/ week['Population'])*100000, 2)
        week.drop(week[week['7-Day Daily {c_or_d} per 100,000 as of {date}'.format(c_or_d = c_or_d, date = date)] < 0].index, inplace = True)
        week = week.reset_index(drop = True)
        
        return week
    
    cs = week_compiler(cases, 'Cases')
    ds = week_compiler(deaths, 'Deaths')
    
    covid_data = cs[cs.columns[:4]]
       
    cs.drop(ds.columns[[0,2,3]], axis = 1, inplace = True)
    ds.drop(ds.columns[[0,2,3]], axis = 1, inplace = True)
        
    for i in range(1,8):
        covid_data = pd.merge(covid_data, cs[cs.columns[[0,i]]], on = 'County Name')
        covid_data = pd.merge(covid_data, ds[ds.columns[[0,i]]], on = 'County Name')
        
    covid_data = covid_data.rename(columns = {'countyFIPS': 'County FIPS'})

    return covid_data

def create_vaxx_data():
    def data():
        data = pd.read_csv('CDC VACCINE COUNTY DATA DOWNLOAD LINK')

        no_mo = {1:'January',
                 2:'February',
                 3:'March',
                 4:'April',
                 5:'May',
                 6:'June',
                 7:'July',
                 8:'August',
                 9:'September',
                 10:'October',
                 11:'November',
                 12:'December'
             }

        latest_date = data['Date'][0]

        def word_name(date):
            month, day, year = [int(value) for value in date.split('/')]
            date = '{month} {day}, {year}'.format(month = no_mo[month], day = day, year = year)

            return date

        date = word_name(latest_date)

        data['Recip_County'] = data['Recip_County'] + ', ' + data['Recip_State']

        dates = list(data['Date'])

        def get_months():

            m_dates = []

            l_month = 0

            for date in dates:
                month = int(date.split('/')[0])
                if month != l_month:
                    m_dates.append(date)
                l_month = month

            return m_dates

        data = data[data['Date'].isin(get_months())]

        for col in data.columns:
            if col != 'Recip_County' and 'Pct' not in col and col != 'Date':
                data.drop(col, axis = 1, inplace = True)

        data.columns = ['Date', 'County Name', '% Fully Vaccinated as of {}'.format(date),'% ≥ 12 Fully Vaccinated as of {}'.format(date), '% ≥ 18 Fully Vaccinated as of {}'.format(date), '% ≥ 65 Fully Vaccinated as of {}'.format(date)]

        dates = list(data['Date'])

        data = data.iloc[::-1]

        data.reset_index(drop = True, inplace = True)

        data['Date'] = data['Date'].apply(lambda date: word_name(date))
        
        return data

    data = data()
    
    filename = 'FILE NAME'
    bucketname = 'BUCKET NAME'
    
    csv_buffer = StringIO()
    data.to_csv(csv_buffer)
    
    client = boto3.client('s3')
    
    response = client.put_object(Body = csv_buffer.getvalue(), Bucket = bucketname, Key = filename)

def combiner():
    
    race_data = create_race_data()
    inc_unemp_data = create_inc_unemp_data()
    edu_data = create_edu_data()
    mask_data = create_mask_data()
    covid_data = create_covid_pop_data()
    
    # VAXX DATA

    # puts vaxx data into bucket

    create_vaxx_data()

    # Reads vaxx data

    vaxx_data = readbucketdata.readbucketdata('CHOICE')

    date = list(vaxx_data['Date'])[-1]

    vaxx_data = vaxx_data[vaxx_data['Date'] == date].drop('Date', axis = 1).reset_index(drop = True)
    
    # Combines all

    county_data = pd.merge(covid_data, inc_unemp_data, on = 'County Name')
    county_data = pd.merge(county_data, race_data, on = 'County Name')
    county_data = pd.merge(county_data, edu_data, on = 'County Name')
    county_data = pd.merge(county_data, mask_data, on = 'State')
    county_data = pd.merge(county_data, vaxx_data, on = 'County Name')

    return county_data

def main_function():
    data = combiner()
    
    filename = 'FILE NAME'
    bucketname = 'BUCKET NAME'
    
    csv_buffer = StringIO()
    data.to_csv(csv_buffer)
    
    client = boto3.client('s3')
    
    response = client.put_object(Body = csv_buffer.getvalue(), Bucket = bucketname, Key = filename)

if __name__ == '__main__':
    main_function()
