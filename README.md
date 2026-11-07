# WQU A/B Testing Dashboard 

![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-Plotly-008DE4?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458?style=for-the-badge&logo=pandas&logoColor=white)

An end-to-end Extract, Transform, Load (ETL) and A/B Testing Web Application built with Python, Dash, and MongoDB. This project analyzes applicant demographics and runs live statistical simulations (Chi-Square tests) to evaluate the effectiveness of an email campaign on admissions quiz completion rates.

##  Features

The application is divided into three core sections:
1. **Applicant Demographics:** Interactive visualizations of applicant data, including a global Nationality Map (Choropleth), Age Distribution Histogram, and Education Level Bar Chart.
2. **Experiment Configuration:** A statistical power calculator where users can adjust the Minimum Detectable Effect Size to determine the required sample size for the A/B test.
3. **Simulation & Results:** A live Chi-Square test executor that evaluates control vs. treatment groups, outputting the Chi-Square statistic, P-Value, a plain-English statistical verdict, and a clustered contingency bar chart.

## Architecture 

This project follows a strict **Three-Tier Architecture**:
* **Database Layer (`repository.py`):** Handles secure connections to MongoDB Atlas and translates raw NoSQL document queries into clean, wide-format Pandas DataFrames.
* **Business Logic Layer (`stats.py` & `visuals.py`):** Calculates statistical power, executes SciPy chi-square tests, and generates Plotly figures.
* **Presentation Layer (`app.py`):** Manages the Dash UI layout, user inputs, and callback routing.

## Repository Structure

```text
wqu_ab_testing/
├── Datafiles/               # Raw and processed datasets
├── Notebooks/               # Jupyter notebooks for exploratory data analysis
├── Scripts/                 # Standalone ETL or utility scripts
├── ab_test_dashboard/       # Main Dash web application
│   ├── .gitignore           # Protects secrets from version control
│   ├── requirements.txt     # Production dependencies
│   ├── repository.py        # MongoDB connection and queries
│   ├── stats.py             # Chi-square and power calculations
│   ├── visuals.py           # Plotly graph generation
│   └── app.py               # Dash layout and callbacks
└── README.md
```

## Tech Stack

* **Frontend:** Dash (Plotly)
* **Backend:** Python, Flask (via Dash), Gunicorn (Production Server)
* **Data Processing:** Pandas, PyMongo, PyCountry
* **Statistics:** SciPy, Statsmodels
* **Database:** MongoDB Atlas

## Local Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/wqu_ab_testing.git
   cd wqu_ab_testing/ab_test_dashboard
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file inside the `ab_test_dashboard` directory with your MongoDB Atlas credentials:
   ```env
   DB_USERNAME="your_mongodb_username"
   DB_PASSWORD="your_mongodb_password"
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://127.0.0.1:8050/`.

## Deployment

This application is configured for seamless deployment on **Render.com**. 
* **Root Directory:** `ab_test_dashboard`
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `gunicorn app:server`
*(Note: Ensure `DB_USERNAME` and `DB_PASSWORD` are added to Render's Environment Variables).*
