# 🏎️ F1 StrategyLab – Race Strategy & Performance Intelligence

**An interactive Formula 1 analytics dashboard that transforms race data into meaningful performance insights and strategy recommendations.**

<p align="center">
  <a href="https://f1-strategylab.streamlit.app/">
    <img src="https://img.shields.io/badge/Live%20Dashboard-Visit%20App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Dashboard">
  </a>
  <a href="https://github.com/muthumalar2301-lily/F1-StrategyLab">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github" alt="GitHub Repository">
  </a>
</p>

---

## 📌 Project Overview

F1 StrategyLab is a sports analytics project designed to explore Formula 1 race performance, tyre strategies, pit-stop efficiency, and driver comparisons through an interactive data visualization dashboard.

Using historical race data from the **2024 British Grand Prix at Silverstone Circuit**, the application analyzes multiple aspects of race performance and presents the findings through interactive charts, performance metrics, and automated strategy insights.

The project demonstrates how data analytics and visualization can be applied to motorsports to better understand race strategies and driver performance.

## 🎯 Project Objectives

* Analyze individual driver performance and lap-time consistency.
* Investigate tyre compound usage and stint strategies.
* Evaluate pit-stop performance and timing.
* Compare race strategies across different drivers.
* Examine tyre degradation patterns.
* Generate automated insights from historical race data.
* Present complex race information through an interactive dashboard.

## ✨ Key Features

### 1. Race Overview

* Overall race statistics and key performance indicators.
* Driver participation and lap-count visualization.
* Track and air temperature analysis.
* General race performance overview.

### 2. Driver Performance Analysis

* Driver-wise average lap times.
* Fastest lap comparisons.
* Total completed laps.
* Team and driver performance breakdown.

### 3. Tyre Strategy Analysis

* Distribution of tyre compounds used.
* Average stint length by compound.
* Tyre usage patterns.
* Comparison of different tyre strategies.

### 4. Pit Stop Analysis

* Driver-wise pit-stop statistics.
* Average pit duration.
* Fastest recorded pit duration.
* Pit-stop performance comparisons.

### 5. Strategy Insights

* Comparison of driver stint strategies.
* Number of stints completed.
* Race distance covered.
* Insights into tyre compound usage.

### 6. Advanced Analytics

* Tyre degradation analysis based on tyre age.
* Compound-wise lap-time trends.
* Driver strategy comparisons.
* Detailed pit-stop timing analysis.

### 7. Strategy Recommendations

* Automated insights based on tyre performance.
* Identification of the longest recorded tyre stint.
* Fastest recorded pit duration.
* Driver strategy comparisons.

### 8. Driver Comparison

* Interactive selection of two drivers.
* Lap-time comparison throughout the race.
* Average lap-time comparison.
* Fastest lap comparison.
* Total laps completed by each selected driver.

## 🛠️ Technology Stack

| Technology                | Purpose                                    |
| ------------------------- | ------------------------------------------ |
| Python                    | Core programming and data processing       |
| Pandas                    | Data manipulation and analysis             |
| NumPy                     | Numerical operations                       |
| Plotly                    | Interactive data visualizations            |
| Streamlit                 | Interactive dashboard development          |
| Requests                  | API data extraction                        |
| OpenF1 API                | Historical Formula 1 race data             |
| Git & GitHub              | Version control and source code management |
| Streamlit Community Cloud | Application deployment                     |

## 📊 Dataset Information

The project uses historical Formula 1 data from the **2024 British Grand Prix**, held at Silverstone Circuit.

### Data Source

[OpenF1 API](https://openf1.org/)

OpenF1 provides access to Formula 1 session information, lap timings, driver details, tyre stints, pit-stop information, and weather conditions.

### Datasets Used

| Dataset       | Description                                        |
| ------------- | -------------------------------------------------- |
| Lap Data      | Lap numbers, lap durations, and driver information |
| Stint Data    | Tyre compounds, stint numbers, and stint durations |
| Pit Stop Data | Pit-stop lap numbers and timing information        |
| Weather Data  | Track temperature, air temperature, and humidity   |
| Driver Data   | Driver names, numbers, and team information        |

The extracted datasets are stored locally as CSV files for analysis and dashboard visualization.

## 📁 Project Structure

```text
F1-StrategyLab/
│
├── app.py
│
├── data/
│   ├── raw/
│   │   ├── laps.csv
│   │   ├── stints.csv
│   │   ├── pitstops.csv
│   │   ├── weather.csv
│   │   └── drivers.csv
│   │
│   └── processed/
│       ├── lap_data.csv
│       ├── stint_data.csv
│       ├── pitstop_data.csv
│       └── weather_data.csv
│
├── modules/
│   ├── data_loader.py
│   ├── analysis.py
│   └── recommendation.py
│
├── requirements.txt
├── test_data.py
├── .gitignore
└── README.md
```

## ⚙️ Installation & Setup

Follow these steps to run F1 StrategyLab locally.

### Prerequisites

* Python 3.9 or above
* Git
* A code editor such as Visual Studio Code

### 1. Clone the Repository

```bash
git clone https://github.com/muthumalar2301-lily/F1-StrategyLab.git
```

### 2. Navigate to the Project Directory

```bash
cd F1-StrategyLab
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at:

```text
http://localhost:8501
```

## 📦 Dependencies

The project uses the following Python libraries:

```text
streamlit
pandas
numpy
plotly
requests
```

These dependencies are listed in `requirements.txt`.

## 🌐 Live Deployment

The application is deployed using Streamlit Community Cloud.

**Explore the live dashboard:**

### 👉 https://f1-strategylab.streamlit.app/

No local installation is required to explore the deployed application.

## 🔍 Analytical Approach

The project follows a structured analytics workflow:

1. **Data Collection:** Retrieve historical Formula 1 race data using the OpenF1 API.
2. **Data Processing:** Organize, clean, and transform the extracted datasets using Pandas.
3. **Exploratory Analysis:** Examine driver performance, tyre usage, pit stops, and weather conditions.
4. **Performance Analysis:** Calculate lap-time statistics, stint lengths, and tyre degradation trends.
5. **Insight Generation:** Derive automated observations from race performance metrics.
6. **Visualization:** Present analytical findings through interactive Plotly charts and Streamlit components.
7. **Deployment:** Publish the dashboard using Streamlit Community Cloud.

## 🚀 Future Enhancements

Potential improvements include:

* Support for multiple Formula 1 seasons and Grand Prix events.
* Real-time race data integration.
* Predictive tyre degradation modelling.
* Machine learning-based pit-stop strategy recommendations.
* Safety car and weather impact analysis.
* Advanced driver performance benchmarking.
* More comprehensive race strategy simulations.

## ⚠️ Limitations

* The current implementation focuses on the 2024 British Grand Prix.
* Strategy insights are derived from historical data and descriptive analytics.
* Lap-time comparisons can be affected by traffic, weather, safety cars, and other race conditions.
* Automated recommendations should be interpreted as analytical observations rather than definitive race strategy decisions.

## 👩‍💻 Author

**Muthu Malar**

GitHub: [@muthumalar2301-lily](https://github.com/muthumalar2301-lily)

Project: [F1 StrategyLab](https://github.com/muthumalar2301-lily/F1-StrategyLab)

Live Application: [F1 StrategyLab Dashboard](https://f1-strategylab.streamlit.app/)

---

<p align="center">
  <b>Turning Formula 1 Race Data into Strategic Insights. 🏁</b>
</p>
