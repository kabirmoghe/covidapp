### Live COVID-19 WebApp

This application provides information on a granular level about the spread and local impact of COVID-19. The app allows users to understand the current situation of the pandemic in their county, understand vaccination data, and explore the relationship between various county attributes and COVID-19 data.
Sources

The self-updating data set compiles data from the sources below:

Cumulative COVID-19 Case and Death Tallies: [USAFacts](https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/)

Vaccinations: [CDC](https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-County/8xkx-amqh)

Mask/Social-Distancing Policies: [AARP](https://www.aarp.org/health/healthy-living/info-2020/states-mask-mandates-coronavirus.html)

Race Demographics: [US Census Bureau](https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/counties/totals/)

Unemployment, Income, and Education: [USDA](https://www.ers.usda.gov/data-products/county-level-data-sets/download-data/)

Calculated Population Density: [USAFacts](https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/) and [ArcGIS](https://hub.arcgis.com/datasets/esri::usa-counties/about)

Methodology

In order to determine the "risk of infection" in a certain county, the 7-Day [rolling average](https://www.georgiaruralhealth.org/blog/what-is-a-moving-average-and-why-is-it-useful/) was used, which is the average number of new cases each day over the past week per 100,000 people. Since county-wide population varies, 100,000 is a commonly used number to have normalized rates across all counties, so simple percentages are scaled to a number of cases out of 100,000.

To calculate risk from the rolling average, the methods from the [Harvard Global Health Institute](https://ethics.harvard.edu/files/center-for-ethics/files/key_metrics_and_indicators_v4.pdf) were used. Specifically, as shown by the "../static/risk_labeled.png," "low" risk (green) was determined as < 1 new cases per day, "moderately low" risk (yellow) as 1 or more but less than 10 new cases per day, "moderately high" risk (orange) as 10 or more but less than 25 new cases per day, and "high" risk (red) as 25 or more new cases per day (all according to the 7-day rolling average).
