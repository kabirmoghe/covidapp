import numpy as np
import pandas as pd
import requests
import json
from urllib.request import urlopen
import plotly.express as px
import plotly.graph_objects as go

def county_list():
    ctys = list(pd.read_csv('https://raw.githubusercontent.com/kabirmoghe/Demographic-Data/main/countynames.csv')['County Name'].values)
    return ctys

def county_stats(county_name):
    if county_name == '':
        return "Please enter a county name (i.e. Orange County, CA)."
    else:
        data = pd.read_csv('fulldataset.csv', index_col = 0)
        vaxx_data = pd.read_csv('vaxxdataset.csv', index_col = 0)

        data['County FIPS'] = data['County FIPS'].apply(lambda value: '0' + str(value) if len(str(value)) == 4 else str(value))

        #infs = [column for column in data.columns if "Infection" in column.split() and "Cumulative" not in column.split() and "Predicted" not in column.split()]

        cols = data.columns

        inf_col = 0
        for col in cols:
            if "Cases" in col.split() and "per" in col.split():
                inf_col = col


        sorted_data = data.sort_values(by = inf_col, ascending = False)[['County Name', inf_col]].reset_index(drop = True)

        ctynum = len(sorted_data)

        high25pct = round(ctynum*0.25)
        low25pct = round(ctynum*0.75)

        #sets thresholds for different COVID risk levels

        green = 1 # low
        yellow = 10 # moder. low
        orange = 25 # moder. high

        #red is greater than 25, high


        '''county_df = data[data['County Name'] == county_name][infs].transpose().reset_index()
        county_df['Time'] = ["Jan '20", "Feb '20", "Mar '20", "Apr '20", "May '20", "Jun '20", "Jul '20", "Aug '20", "Sept '20", "Oct '20", "Nov '20", "Dec '20", "Jan '21", "Feb '21", "Mar '21", "Apr '21", "May '21"]
        county_df['Infection Rate per 100,000 for {county_name}'.format(county_name = county_name)] = county_df.iloc[:,1]
            
        sns.barplot(x = "Time", y = 'Infection Rate per 100,000 for {county_name}'.format(county_name = county_name), data = county_df, palette = 'plasma').get_figure()
        plt.savefig('/app/static/countyplot.png')
        '''
        des_row = data[data['County Name'] == str(county_name)]

        des_row.rename(index = {des_row.index.values[0]: county_name}, inplace = True)

        mask_info= [des_row[col].values[0] for col in des_row.columns if 'mask' in col.lower()]

        y_n_mask, mask_details = mask_info

        des_row.drop('Mask Mandate Details', axis = 1, inplace = True)

        otherinfo = pd.concat([des_row['Population'], des_row.iloc[:, -15:]], axis = 1)

        stat = des_row[inf_col].iloc[0]

        rank = sorted_data[sorted_data['County Name']==county_name].index[0]+1

        css_prop = stat/27

        if css_prop <= 1:
            css_prop = css_prop
        else:
            css_prop = 1.0

        #pct = round(prop*100,2)

        prop = (1-(rank/len(sorted_data)))

        pct = round(prop*100, 2)


        if stat == 0.0:
            rec = '{county_name} has a low risk of infection and is on track for containment. Regardless, some precaution should be taken and the guidelines below should be followed (see details below).'.format(county_name = county_name)
                
            color = '#7cff02'

            info = "With a rank of {rank} out of {ctynum} included counties, {county_name} is one of the lowest counties in terms of {inf_col}.".format(rank = rank, ctynum = ctynum, county_name = county_name, pct = pct, inf_col = inf_col)
            
            risk = 'Low'

        elif round(pct) == 100.0:
            rec = 'There is a high risk of infection in {county_name}, so precaution should be taken and guidelines should be followed strictly (see details below).'.format(county_name = county_name)
                
            color = '#ff0600'

            info = "With a rank of {rank} out of {ctynum} included counties, {county_name} is the highest county in terms of {inf_col}.".format(rank = rank, ctynum = ctynum, county_name = county_name, pct = pct, inf_col = inf_col)
            
            risk = 'High'

        else:
            if stat < green:
                rec = '{county_name} has a low risk of infection and is on track for containment. Regardless, some precaution should be taken and guidelines should be followed (see details below).'.format(county_name = county_name)

                color = '#7cff02'

                risk = 'Low'

            elif green <= stat < yellow:
                rec = '{county_name} has a moderately low risk of infection, and strategic choices must be made about which package of non-pharmaceutical interventions to use for control. Precaution should be still be taken and guidelines should be followed (see details below).'.format(county_name = county_name)
                    
                color = '#fff800'

                risk = 'Moderately Low'

            elif yellow <= stat < orange:
                rec = '{county_name} has a moderately high risk of infection, and strategic choices must be made about which package of non-pharmaceutical interventions to use for control. Stay-at-home orders are advised unless viral testing and contact tracing capacity are implementable at levels meeting surge indicator standards. Precaution should be taken and guidelines should be followed (see details below).'.format(county_name = county_name)

                color = '#ffab00'

                risk = 'Moderately High'

            else:
                rec = '{county_name} has a high risk of infection, and stay-at-home orders may be necessary. Extra precaution should be taken and guidelines should be followed (see details below).'.format(county_name = county_name)

                color = '#ff0600'

                risk = 'High'

            info = "With a rank of {rank} out of {ctynum} included counties, {county_name} is higher than {pct}% of counties in terms of {inf_col}.".format(rank = rank, ctynum = ctynum, county_name = county_name, pct = pct, inf_col = inf_col)

        riskimg = 'riskchart.png'
        risk_pos = (round(26.5+(49*css_prop),2))
                
        return otherinfo, stat, info, rec, risk_pos, pct, y_n_mask, mask_details, color, risk#, riskimg
        
def usplot(c_or_d):
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    
    data = pd.read_csv('fulldataset.csv', index_col = 0)
    
    data = data[data['State'] != 'NE']
    data = data[data['State'] != 'FL']

    data['County FIPS'] = data['County FIPS'].apply(lambda value: '0' + str(value) if len(str(value)) == 4 else str(value))
    if c_or_d == 'c':

        last_case_rate = [column for column in data.columns if "Cases" in column.split() and "per" in column.split()][0]
        
        date = last_case_rate.split('as of ')[1]

        num0 = len(data[data[last_case_rate] == 0])

        fig = px.choropleth(data, geojson=counties, locations='County FIPS', color=last_case_rate,
                               color_continuous_scale=['#3EAC58', '#F6E520','#F6E520','#F6E520','#F6E520', '#ED9A0C', '#ED9A0C','#ED9A0C', '#ED9A0C', '#ED9A0C','#E64B01'],
                               hover_name = 'County Name',
                               hover_data=[last_case_rate, 'Population'],
                               scope="usa", range_color=[0,25],
                               labels={last_case_rate:'Infection Risk (Daily Cases per 100k)'}

                               )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, font_family = "Raleway", hoverlabel_font_family = "Raleway")
        fig.update_traces(marker_line_width=0, marker_opacity=0.8, hoverlabel_bgcolor='#e3f1ff', hoverlabel_bordercolor = '#e3f1ff', hoverlabel_font_color='#000066')
        fig.update_geos(showsubunits=True, subunitcolor="black", subunitwidth = 1.4)
        fig.write_html("/app/templates/c_usplot.html", full_html = False)
        
        sorted_data = data.sort_values(by = last_case_rate, ascending = False)[['County Name', last_case_rate]].reset_index(drop = True)

        top10 = sorted_data.head(10)[['County Name', last_case_rate]].reset_index(drop = True)
        bot10 = sorted_data.tail(10)[['County Name', last_case_rate]].reset_index(drop = True)

    else:

        last_death_rate = [column for column in data.columns if "Deaths" in column.split() and "per" in column.split()][0]

        date = last_death_rate.split('as of ')[1]

        def log_maker(value):
            if value != 0:
                if np.log(value) < 0:
                    return 0
                else:
                    return np.log(value)
            else:
                return value

        data['Log {name}'.format(name = last_death_rate)] = data[last_death_rate].apply(lambda value: log_maker(value))

        num0 = len(data[data[last_death_rate] == 0])
        
        fig = px.choropleth(data, geojson=counties, locations='County FIPS', color='Log {name}'.format(name = last_death_rate),
                               color_continuous_scale="Plasma",
                               hover_name = 'County Name',
                               hover_data=[last_death_rate, 'Population'],
                               scope="usa",
                               labels={'Log {name}'.format(name = last_death_rate):'Current Log. Daily Deaths per 100k'}
                              )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, font_family = "Raleway", hoverlabel_font_family = "Raleway")
        fig.update_traces(marker_line_width=0, marker_opacity=0.8, hoverlabel_bgcolor='#e3f1ff', hoverlabel_bordercolor = '#e3f1ff', hoverlabel_font_color='#000066')
        fig.update_geos(showsubunits=True, subunitcolor="black", subunitwidth = 1.4)
        fig.write_html("/app/templates/d_usplot.html", full_html = False)

        sorted_data = data.sort_values(by = last_death_rate, ascending = False)[['County Name', last_death_rate]].reset_index(drop = True)

        top10 = sorted_data.head(10)[['County Name', last_death_rate]].reset_index(drop = True)
        bot10 = sorted_data.tail(10)[['County Name', last_death_rate]].reset_index(drop = True)

    #top10lst = []
    
    #for i in range(10):
    #    top10lst.append('{cty}: {stat}'.format(cty = top10['County Name'].iloc[i], stat = round(float(top10[inf_col].iloc[i]),2)))

    return top10, bot10, date, num0

def avg_plot(cty):

    data = pd.read_csv('fulldataset.csv')
    data = pd.concat([data['County Name'], data[[col for col in data.columns if 'Cases' in col and 'Moving Avg.' in col]]], axis = 1)

    data = data[data['County Name'] == cty]

    data = data.transpose().iloc[1:].reset_index()

    data.columns = ['Date', 'Moving Avg']

    data['Date (Week of)'] = data['Date'].apply(lambda value: value.split('Avg. ')[-1])
    data.drop('Date', axis = 1, inplace = True)

    yval = 3

    for value in data['Moving Avg']:
        if value >= 25:
            if (value-27)+3 > yval:
                yval = (value-27)+3
            else:
                None
        else:
            None

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['Date (Week of)'], 
        y=[1,1,1,1,1],
        name = 'Low',
        hoverinfo='skip',
        mode='lines',
        line=dict(width=0.5, color='#69F68C'),
        stackgroup='one' # define stack group
    ))
    
    fig.add_trace(go.Scatter(
        name = 'Mod. Low',
        x=data['Date (Week of)'], 
        y=[9,9,9,9,9],
        hoverinfo='skip',
        mode='lines',
        line=dict(width=0.5, color='#fff800'),
        stackgroup='one' # define stack group
    ))
    
    fig.add_trace(go.Scatter(
        x=data['Date (Week of)'], 
        y=[15,15,15,15,15],
        hoverinfo='skip',
        name = 'Mod. High',
        mode='lines',
        line=dict(width=0.5, color='#ffab00'),
        stackgroup='one' # define stack group
    ))
    
    fig.add_trace(go.Scatter(
        x=data['Date (Week of)'], 
        y=[yval for i in range(5)],
        hoverinfo='skip',
        mode='lines',
        name = 'High',
        line=dict(width=0.5, color='#ff0600'),
        stackgroup='one' # define stack group
    ))
    
    fig.add_trace(go.Scatter(
            name='Moving Avg',
            x=data['Date (Week of)'],
            y=data['Moving Avg'],
            hoverinfo = 'name+y',
            mode = 'lines',
            line=dict(
                color='#64B1FC')
        ))
    
    fig.update_layout(
        yaxis_title='Moving Average', yaxis_range=[0,25+yval], xaxis_title = 'Date (Week of)',
        title='Moving Average Past 5 weeks', title_x = 0.5, font_family="Raleway", hoverlabel_font_family = 'Raleway'
    )


    fig.write_html('/app/templates/{cty}_movingavgplot.html'.format(cty = cty), full_html = False)

def vaxx_plot(cty):
    
    data = pd.read_csv('vaxxdataset.csv', index_col = 0)
    
    data = data[data['County Name'] == cty]
    
    if len(data) == 0:
        return 

    full_date = list(data['Date'])[-1]
    
    data.reset_index(drop = True, inplace = True)
    
    no_mo = {'January':'Jan.',
             'February':'Feb.',
             'March':'Mar.',
             'April':'Apr.',
             'May':'May',
             'June':'Jun.',
             'July':'Jul.',
             'August':'Aug.',
             'September':'Sep.',
             'October':'Oct.',
             'November':'Nov.',
             'December':'Dec.'
         }
    
    def easy_name(date):
        
        date = date.split()
        
        mo = no_mo[date[0]]
        yr = "'{}".format((date[2])[2:])
        
        return '{} {}'.format(mo, yr)
        
    data['Date'] = data['Date'].apply(lambda value: easy_name(value))
    
    date = list(data['Date'])[-1]
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
            name='Target Adults % Fully Vaxx.',
            x=data['Date'],
            hoverinfo = 'y',
            y=[76.51 for i in range(len(data))],
            line=dict(
                color='#FF8195', dash = 'dash', width = 3
            ),
            mode='lines'
        ))
    

    fig.add_trace(go.Scatter(
            name='% Fully Vaccinated',
            x=data['Date'],
            y=data['% Fully Vaccinated as of {}'.format(full_date)],
            marker=dict(
                color='#69F68C')
        ))

    fig.add_trace(go.Scatter(
            name='% 12+ Fully Vaxx.',
            x=data['Date'],
            y=data['% ≥ 12 Fully Vaccinated as of {}'.format(full_date)],
            marker=dict(
                color='#81B8FF')
        ))


    fig.add_trace(go.Scatter(
            name='% 18+ Fully Vaxx.',
            x=data['Date'],
            y=data['% ≥ 18 Fully Vaccinated as of {}'.format(full_date)],
            marker=dict(
                color='#FF8195')
        ))

    fig.add_trace(go.Scatter(
            name='% 65+ Fully Vaxx.',
            x=data['Date'],
            y=data['% ≥ 65 Fully Vaccinated as of {}'.format(full_date)],
            marker=dict(
                color='#FFC300')
        ))
    fig.update_layout(
        yaxis_title='% Fully Vaccinated', yaxis_range=[0,100], xaxis_title = 'Month',
        title='Vaccination Progress for {}, {}'.format(cty, full_date), title_x = 0.5, font_family="Raleway", hoverlabel_font_family = 'Raleway'
    )
    
    #--

    data = pd.read_csv('fulldataset.csv', index_col = 0)

    data = data[data['County Name'] == cty]

    fig2 = go.Figure()    

    fig2.add_trace(go.Bar(
    y=['All'],
    x=data['% Fully Vaccinated as of {}'.format(full_date)],
    width=[0.5],
    name='% Fully Vaxx.',
    orientation='h',
    marker=dict(
        color='#69F68C'
        )
    ))

    fig2.add_trace(go.Bar(
    y=['12+'],
    x=data['% ≥ 12 Fully Vaccinated as of {}'.format(full_date)],
    width=[0.5],
    name='% 12+ Fully Vaxx.',
    orientation='h',
    marker=dict(
        color='#81B8FF',
        )
    ))

    fig2.add_trace(go.Bar(
    y=['18+'],
    x=data['% ≥ 18 Fully Vaccinated as of {}'.format(full_date)],
    width=[0.5],
    name='% 18+ Fully Vaxx.',
    orientation='h',
    marker=dict(
        color='#FF8195',
        )
    ))

    fig2.add_trace(go.Bar(
    y = ['65+'],
    x=data['% ≥ 65 Fully Vaccinated as of {}'.format(full_date)],
    width=[0.5],
    name='% 65+ Fully Vaxx.',
    orientation='h',
    marker=dict(
        color='#FFC300',
        )
    ))

    fig2.update_layout(xaxis_range=[0,100], title ={'text':'Current % Vaccinated, {}'.format(full_date) ,'xanchor': 'center',
        'yanchor': 'top'}, xaxis_title="% People Vaccinated", yaxis_title = 'Age Demographic', font_family="Raleway", hoverlabel_font_family = 'Raleway', title_x=0.5)


    fig.write_html('/app/templates/{cty}_vaxxprogressplot.html'.format(cty = cty), full_html = False)
    fig2.write_html('/app/templates/{cty}_vaxxplot.html'.format(cty = cty), full_html = False)


def multivaxx_plot():
    
    data = pd.read_csv('fulldataset.csv', index_col = 0)

    date = [col for col in data.columns if 'Fully' in col][-1].split('as of ')[1]

    data = data[data['% Fully Vaccinated as of {}'.format(date)] != 0].reset_index(drop = True)

    data['County FIPS'] = data['County FIPS'].apply(lambda value: '0' + str(value) if len(str(value)) == 4 else str(value))

    df_top = data.sort_values(by = '% Fully Vaccinated as of {}'.format(date)).tail(10)[['County Name', '% Fully Vaccinated as of {}'.format(date)]].reset_index(drop = True)
    df_bottom = data.sort_values(by = '% Fully Vaccinated as of {}'.format(date), ascending = False).tail(10)[['County Name', '% Fully Vaccinated as of {}'.format(date)]].reset_index(drop = True)
    
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    #TOP 10

    fig_top = go.Figure()    
    '''
    fig_top.add_trace(go.Bar(
    y=df_top['County Name'],
    x=df_top['% Vaccinated ≥ 65'],
    width=[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    name='% 65+ Fully Vaxx.',
    orientation='h',
    marker=dict(
        color='#FFC300',
        )
    ))

    fig_top.add_trace(go.Bar(
    y=df_top['County Name'],
    x=df_top['% Vaccinated ≥ 18'],
    width=[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    name='% 18+ Fully Vaxx.',
    orientation='h',
    marker=dict(
        color='#FF8195',
        )
    ))

    fig_top.add_trace(go.Bar(
    y=df_top['County Name'],
    x=df_top['% Vaccinated ≥ 12'],
    width=[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    name='% 12+ Fully Vaxx.',
    orientation='h',
    marker=dict(
        color='#81B8FF',
        )
    ))
    '''
    
    fig_top.add_trace(go.Bar(
    y=df_top['County Name'],
    x=df_top['% Fully Vaccinated as of {}'.format(date)],
    width=[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    name='% Fully Vaxx.',
    orientation='h',
    marker=dict(
        color='#69F68C'
        )
    ))
    
    fig_top.update_layout(
    title={
        'text': "Plot Title",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    
    
    fig_top.update_layout(xaxis_range=[0,100], title = {'text':'Counties with Highest Vaxx. Progress','xanchor': 'center',
        'yanchor': 'top'}, hovermode='y', xaxis_title="% People Fully Vaccinated", font_family = "Raleway", hoverlabel_font_family = "Raleway")
    
    fig_top.write_html('/app/templates/multivaxxplot_top.html', full_html = False)

    #BOTTOM 10
    fig_bottom = go.Figure()    
    '''
    fig_bottom.add_trace(go.Bar(
    y=df_bottom['County Name'],
    x=df_bottom['% Vaccinated ≥ 65'],
    width=[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    name='% 65+ Fully Vaxx.',
    orientation='h',
    marker=dict(
        color='#FFC300',
        )
    ))
    
    fig_bottom.add_trace(go.Bar(
    y=df_bottom['County Name'],
    x=df_bottom['% Vaccinated ≥ 18'],
    width=[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    name='% 18+ Fully Vaxx.',
    orientation='h',
    marker=dict(
        color='#FF8195',
        )
    ))

    fig_bottom.add_trace(go.Bar(
    y=df_bottom['County Name'],
    x=df_bottom['% Vaccinated ≥ 12'],
    width=[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    name='% 12+ Fully Vaxx.',
    orientation='h',
    marker=dict(
        color='#81B8FF',
        )
    ))
    '''
    fig_bottom.add_trace(go.Bar(
    y=df_bottom['County Name'],
    x=df_bottom['% Fully Vaccinated as of {}'.format(date)],
    width=[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    name='% Fully Vaxx.',
    orientation='h',
    marker=dict(
        color='#EC7063'
        )
    ))
    
    fig_bottom.update_layout(
    title={
        'text': "Plot Title",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    
    
    fig_bottom.update_layout(xaxis_range=[0,100], title = {'text':'Counties with Lowest Vaxx. Progress','xanchor': 'center',
        'yanchor': 'top'}, hovermode='y', xaxis_title="% People Fully Vaccinated", font_family = "Raleway", hoverlabel_font_family = "Raleway")
    
    fig_bottom.write_html('/app/templates/multivaxxplot_bottom.html', full_html = False)
    
    fig_map = px.choropleth(data, geojson=counties, locations='County FIPS', color='% Fully Vaccinated as of {}'.format(date),
                           color_continuous_scale=['#FF3C33', '#FBF30B', '#41B26A'],
                           hover_name = 'County Name',
                           hover_data=['Population','% ≥ 12 Fully Vaccinated as of {}'.format(date), '% ≥ 18 Fully Vaccinated as of {}'.format(date), '% ≥ 65 Fully Vaccinated as of {}'.format(date)],
                           scope="usa",
                           labels={'% Fully Vaccinated as of {}'.format(date):'Current % Fully Vaccinated', '% ≥ 12 Fully Vaccinated as of {}'.format(date):'Current % 12+ Fully Vaccinated', '% ≥ 18 Fully Vaccinated as of {}'.format(date):'Current % 18+ Fully Vaccinated', '% ≥ 65 Fully Vaccinated as of {}'.format(date):'Current % 65+ Fully Vaccinated'}
                          )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, font_family = "Raleway", hoverlabel_font_family = "Raleway")
    fig_map.update_traces(marker_line_width=0, marker_opacity=0.8, hoverlabel_bgcolor='#e3f1ff', hoverlabel_bordercolor = '#e3f1ff', hoverlabel_font_color='#000066')
    fig_map.update_geos(showsubunits=True, subunitcolor="black", subunitwidth = 1.4)

    fig_map.write_html('/app/templates/us_vaxxmap.html', full_html = False)

    return date


def scatter(x, y, trendline):

    data = pd.read_csv('fulldataset.csv', index_col = 0)
    vaxx_col = [col for col in data.columns if "Fully" in col and "≥" not in col][0]
    data = data[data[vaxx_col] != 0]
    
    if trendline == 'y': 
        fig = px.scatter(data_frame = data, x = x, y=y, trendline="ols", labels={
                     "x": x,
                     "y": y}, title="Scatterplot of {} and {}".format(x, y),
                     hover_name = 'County Name')
    else:
        fig = px.scatter(data_frame = data, x=x, y=y, labels={
                     "x": x,
                     "y": y}, title="Scatterplot of {} and {}".format(x, y),
                     hover_name = 'County Name')
    fig.update_layout(font_family = "Raleway", hoverlabel_font_family = "Raleway", title_x = 0.5)
    
    fig.write_html('/app/templates/{}_{}_{}.html'.format(trendline, x, y), full_html = False)
