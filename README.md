\# 📈 Forecasting Financial Inclusion in Ethiopia



\## Overview



This project develops a forecasting system that tracks Ethiopia's digital financial transformation using time series analysis, event-impact modeling, and interactive visualizations. The objective is to forecast the country's financial inclusion progress for 2025–2027 by analyzing historical financial inclusion indicators, policy interventions, product launches, and infrastructure developments.



The project was completed as part of the 10 Academy AI Mastery Program.



\---



\## Business Problem



Ethiopia's financial sector has undergone significant digital transformation through initiatives such as:



\- Telebirr

\- M-Pesa Ethiopia

\- EthSwitch interoperability

\- National Financial Inclusion Strategy (NFIS-II)

\- Fayda Digital ID



Despite rapid mobile money adoption, financial inclusion has grown more slowly than expected.



This project answers the following questions:



\- What factors drive financial inclusion in Ethiopia?

\- How do policies, product launches, and infrastructure investments influence financial inclusion?

\- How will Account Ownership and Digital Payment Usage evolve in 2025–2027?



\---



\## Objectives



\- Explore and enrich Ethiopia's financial inclusion dataset

\- Perform Exploratory Data Analysis (EDA)

\- Model the impact of major financial events

\- Forecast financial inclusion indicators

\- Build an interactive Streamlit dashboard for stakeholders



\---



\## Project Structure



ethiopia-fi-forecast/

│

├── .github/

│   └── workflows/

│       └── unittests.yml

│

├── data/

│   ├── raw/

│   └── processed/

│

├── notebooks/

│

├── src/

│

├── dashboard/

│   └── app.py

│

├── models/

│

├── reports/

│   └── figures/

│

├── tests/

│

├── requirements.txt

├── README.md

└── .gitignore

\---



\## Dataset



The project uses a unified financial inclusion dataset containing:



\- Financial inclusion observations

\- National policy events

\- Product launches

\- Infrastructure milestones

\- Event-impact relationships

\- Government targets



Additional datasets were incorporated during the enrichment phase using trusted sources including:



\- World Bank Global Findex

\- National Bank of Ethiopia

\- Ethio Telecom

\- GSMA

\- IMF Financial Access Survey

\- EthSwitch

\- Fayda Digital ID



\---



\## Workflow



\### Task 1 — Data Exploration \& Enrichment



\- Loaded and explored the unified dataset

\- Understood the data schema

\- Added additional observations and events

\- Documented all enrichment sources

\- Created an enriched dataset



\---



\### Task 2 — Exploratory Data Analysis



Performed analysis on:



\- Financial inclusion trends

\- Account ownership growth

\- Digital payment adoption

\- Infrastructure indicators

\- Event timelines

\- Correlation analysis

\- Data quality assessment



Key outputs include:



\- Time-series visualizations

\- Growth analysis

\- Correlation heatmaps

\- Event timeline

\- Insight summary



\---



\### Task 3 — Event Impact Modeling



Built models to estimate how events affect financial inclusion indicators.



The analysis includes:



\- Event-Indicator association matrix

\- Lag effect modeling

\- Comparable country evidence

\- Historical validation

\- Assumption documentation



\---



\### Task 4 — Forecasting



Forecasted the following indicators:



\- Account Ownership Rate (Access)

\- Digital Payment Usage



Forecast horizon:



\- 2025

\- 2026

\- 2027



Scenarios generated:



\- Baseline

\- Optimistic

\- Pessimistic



Forecast uncertainty is represented using confidence intervals.



\---



\### Task 5 — Interactive Dashboard



Developed a Streamlit dashboard featuring:



\- Financial inclusion overview

\- Interactive trend analysis

\- Event impact visualization

\- Forecast explorer

\- Scenario comparison

\- Downloadable data



\---



\## Technologies Used



\- Python

\- Pandas

\- NumPy

\- Matplotlib

\- Plotly

\- Seaborn

\- Statsmodels

\- Scikit-learn

\- Streamlit

\- Jupyter Notebook

\- Git \& GitHub



\---



\## Installation



Clone the repository



git clone https://github.com/Gelilaaah/ethiopia-fi-forecast.git

Move into the project directory



cd ethiopia-fi-forecast

Create a virtual environment



python -m venv venv

Activate the environment



Windows



venv\\Scripts\\activate

Linux/Mac



source venv/bin/activate

Install dependencies



pip install -r requirements.txt

\---



\## Running the Dashboard



Launch the Streamlit dashboard:



streamlit run dashboard/app.py

\---



\## Results



The project provides:



\- Enriched financial inclusion dataset

\- Exploratory analysis of Ethiopia's digital finance ecosystem

\- Event-impact association matrix

\- Forecasts for 2025–2027

\- Interactive dashboard for policymakers and stakeholders



\---



\## Future Improvements



\- Incorporate quarterly financial inclusion data

\- Use advanced forecasting models such as Prophet and LSTM

\- Integrate real-time financial indicators

\- Expand regional-level forecasting

\- Include macroeconomic variables



\---



\## References



\- World Bank Global Findex

\- IMF Financial Access Survey

\- National Bank of Ethiopia

\- Ethio Telecom

\- GSMA State of the Industry Report

\- EthSwitch

\- Fayda Digital ID

\- Streamlit Documentation

\- Statsmodels Documentation



