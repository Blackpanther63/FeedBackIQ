# 📊 FeedBackIQ – AI Powered Product Review Analyzer

<div align="center">

# 🛍️ FeedBackIQ

### AI-Powered Product Review Analyzer & Sales Impact Prediction Platform

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?style=for-the-badge&logo=flask)
![Selenium](https://img.shields.io/badge/Selenium-Web%20Scraping-green?style=for-the-badge&logo=selenium)
![NLTK](https://img.shields.io/badge/NLTK-Natural%20Language-yellow?style=for-the-badge)
![HTML5](https://img.shields.io/badge/HTML5-orange?style=for-the-badge&logo=html5)
![CSS3](https://img.shields.io/badge/CSS3-blue?style=for-the-badge&logo=css3)
![JavaScript](https://img.shields.io/badge/JavaScript-yellow?style=for-the-badge&logo=javascript)
![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)

An AI-powered web application that extracts product reviews from popular e-commerce platforms, performs sentiment analysis, predicts the business impact of customer feedback, and generates interactive analytical reports.

</div>

---

# 📑 Table of Contents

- Project Overview
- Problem Statement
- Objectives
- Key Features
- Project Workflow
- System Architecture
- Technology Stack
- Software Requirements
- Tools Used
- Screenshots
- Installation
- Future Scope
- Contributors

---

# 📖 Project Overview

**FeedBackIQ** is an intelligent review analysis platform developed using **Flask**, **Python**, **Selenium**, and **Natural Language Processing (NLP)**.

The application automatically extracts customer reviews from e-commerce websites, classifies them into **Positive**, **Negative**, and **Neutral** sentiments using **VADER Sentiment Analysis**, predicts the possible impact on product sales, and presents the results through an interactive dashboard.

The system enables businesses and sellers to understand customer feedback without manually reading hundreds or thousands of reviews.

---

# ❗ Problem Statement

Modern e-commerce websites receive a massive number of customer reviews every day.

Reading every review manually is almost impossible.

Businesses face several challenges:

- Understanding customer satisfaction
- Identifying common complaints
- Tracking sentiment trends
- Measuring product performance
- Predicting the business impact of negative reviews

FeedBackIQ automates the complete review analysis process using Artificial Intelligence and NLP.

---

# 🎯 Objectives

- Automate product review collection
- Perform sentiment analysis
- Predict sales impact
- Generate graphical reports
- Help businesses improve products
- Reduce manual review analysis
- Provide actionable customer insights

---

# ⭐ Key Features

## 🌐 Multi-Platform Product Analysis

Supports product review extraction from multiple e-commerce websites.

Examples:

- Amazon
- Flipkart
- Myntra
- Snapdeal

---

## 🤖 AI-Based Sentiment Analysis

Automatically classifies customer reviews into:

- Positive
- Neutral
- Negative

using NLP techniques.

---

## 📈 Sales Impact Prediction

Predicts how customer sentiment may affect future product sales.

---

## 📊 Interactive Dashboard

Displays

- Product Details
- Ratings
- Customer Reviews
- Sentiment Distribution
- Sales Prediction
- Summary Report

---

## 🔍 Web Scraping

Automatically extracts

- Product Name
- Product Image
- Ratings
- Reviews

using Selenium WebDriver.

---

## 📉 Graphical Visualization

Generates

- Pie Charts
- Bar Charts
- Sentiment Graphs
- Review Statistics
- Sales Impact Graphs

---

## ⚡ Fast Analysis

The application automatically processes large numbers of reviews within seconds.

---

## 🌍 User Friendly Interface

Simple Flask web interface with responsive design.

---

# 🔄 Project Workflow

User

↓

Paste Product URL

↓

Flask Backend

↓

Selenium Web Scraper

↓

Extract Product Information

↓

Extract Customer Reviews

↓

Data Cleaning

↓

NLP Processing

↓

VADER Sentiment Analysis

↓

Sales Impact Prediction

↓

Interactive Dashboard

↓

Final Report

---

# 🏗️ System Architecture

```
               User
                 │
                 ▼
        Product URL Input
                 │
                 ▼
         Flask Web Application
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
 Selenium Scraper     Product Details
        │
        ▼
 Customer Reviews
        │
        ▼
 Data Cleaning
        │
        ▼
 NLP Processing
        │
        ▼
 VADER Sentiment Analysis
        │
        ▼
 Sales Prediction Engine
        │
        ▼
 Dashboard + Charts + Report
```

---

# 💻 Technology Stack

## Frontend

- HTML5
- CSS3
- JavaScript

---

## Backend

- Python
- Flask

---

## Web Scraping

- Selenium WebDriver

---

## Artificial Intelligence

- Natural Language Processing
- NLTK
- VADER Sentiment Analysis

---

## Data Visualization

- Matplotlib
- NumPy

---

## Development Tools

- VS Code
- Git
- GitHub
- Chrome Driver

---

# 🖥️ Software Requirements

- Python 3.x
- Google Chrome
- ChromeDriver
- VS Code
- Flask
- Selenium
- NLTK
- NumPy
- Matplotlib

---
# 🛠️ Tools Used

- Git
- GitHub
- VS Code
- Chrome Driver
- Postman
- Browser Developer Tools

---

# 📂 Project Modules

## 1️⃣ Product Input Module

This module allows users to submit a product for analysis.

### Features

- Paste product URL
- Supports multiple e-commerce platforms
- Validates user input
- Sends URL to backend

Input

```
Amazon Product URL
Flipkart Product URL
Myntra Product URL
Snapdeal Product URL
```

Output

```
Validated Product URL
```

---

## 2️⃣ Web Scraping Module

This module is responsible for collecting product information.

### Extracted Data

- Product Name
- Product Image
- Product Rating
- Customer Reviews
- Review Count

### Technologies Used

- Selenium
- Chrome Driver
- Python

---

## 3️⃣ Data Cleaning Module

Before sentiment analysis, reviews are processed.

Operations include

- Removing Symbols
- Removing HTML Tags
- Lowercase Conversion
- Removing Extra Spaces
- Removing Stop Words

---

## 4️⃣ Sentiment Analysis Module

Natural Language Processing is performed using VADER.

Each review is classified as

- 😊 Positive
- 😐 Neutral
- 😞 Negative

Example

Positive Review

```
Excellent product.
Worth every penny.
```

Negative Review

```
Poor quality.
Very disappointed.
```

Neutral Review

```
Average product.
Delivery was on time.
```

---

## 5️⃣ Sales Impact Prediction

FeedBackIQ estimates how customer sentiment may influence product sales.

The system analyses

- Positive Percentage
- Neutral Percentage
- Negative Percentage

and predicts

- Low Risk
- Medium Risk
- High Risk

---

## 6️⃣ Visualization Module

Generates graphical reports.

Charts include

- Pie Chart
- Bar Chart
- Review Distribution
- Sentiment Graph
- Sales Prediction Graph

---

## 7️⃣ Final Dashboard

Displays

- Product Image
- Product Name
- Product Rating
- Positive Reviews
- Negative Reviews
- Neutral Reviews
- Sales Prediction
- Charts
- Customer Feedback

---

# ⚙️ Working Principle

Step 1

User opens FeedBackIQ.

↓

Step 2

Paste Product URL.

↓

Step 3

Flask receives request.

↓

Step 4

Selenium opens website.

↓

Step 5

Product information is extracted.

↓

Step 6

Customer reviews are collected.

↓

Step 7

Reviews are cleaned.

↓

Step 8

NLTK processes text.

↓

Step 9

VADER performs sentiment analysis.

↓

Step 10

Sales prediction is generated.

↓

Step 11

Dashboard displays complete report.

---

# 📸 Project Screenshots

## Home Page

```html
images/home.png
```

---

## Product Input

```html
images/input.png
```

---

## Product Details

```html
images/product.png
```

---

## Sentiment Analysis

```html
images/sentiment.png
```

---

## Dashboard

```html
images/dashboard.png
```

---

## Charts

```html
images/charts.png
```

---

## Sales Prediction

```html
images/prediction.png
```

---

## Final Report

```html
images/report.png
```

---

# 📊 Key Advantages

- Fully Automated Review Analysis

- AI Powered Sentiment Detection

- Sales Impact Prediction

- Interactive Dashboard

- Faster Decision Making

- Easy To Use

- Multi Platform Support

- Business Insights

- Data Visualization

- Better Customer Understanding

---

# ⚠️ Limitations

- Depends on website structure

- Selenium execution time

- Internet required

- Limited platform support

- CAPTCHA may block scraping

- Prediction is sentiment-based

---

# 🌍 Applications

- E-Commerce Companies

- Product Sellers

- Marketing Teams

- Brand Monitoring

- Customer Experience Analysis

- Product Research

- Business Intelligence

- Market Analysis

- Sales Analytics

- Consumer Feedback Analysis

---
# 🚀 Installation Guide

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/Blackpanther63/FeedBackIQ.git
```

---

## 2️⃣ Navigate to Project Directory

```bash
cd FeedBackIQ/UpdatedFeedI
```

---

## 3️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is unavailable:

```bash
pip install flask selenium nltk matplotlib numpy beautifulsoup4 requests webdriver-manager
```

---

## 5️⃣ Download NLTK Resources

```python
import nltk

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("vader_lexicon")
```

---

## 6️⃣ Start Application

```bash
python app.py
```

or

```bash
flask run
```

---

## 7️⃣ Open Browser

```
http://127.0.0.1:5000
```

---

# 📂 Repository Structure

```text
FeedBackIQ
│
├── UpdatedFeedI/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── fonts/
│
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── result.html
│   ├── review.html
│   └── about.html
│
├── app.py
├── analyser.py
├── requirements.txt
├── README.md
├── report/
├── images/
├── uploads/
└── LICENSE
```

---

# 📄 Project Report

<p align="center">

<a href="report/FeedbackIQ_FINAL.pdf">

<img src="report/report_preview.png" width="700">

</a>

</p>

<p align="center">

<b>📥 Click the preview to open the complete project report.</b>

</p>

---

# 🎥 Project Demonstration

<p align="center">

<a href="video/demo.mp4">

<img src="images/video_thumbnail.png" width="750">

</a>

</p>

<p align="center">

<b>▶ Click the thumbnail to watch the project demonstration.</b>

</p>

---

# 🔮 Future Scope

- AI-based Deep Learning Sentiment Analysis
- Real-Time Product Monitoring
- Multi-language Review Analysis
- Product Recommendation Engine
- Competitor Comparison Dashboard
- Cloud Deployment
- PDF & Excel Report Export
- User Authentication
- Saved Analysis History
- Email Notifications
- Admin Dashboard
- Advanced Data Analytics
- Machine Learning Sales Forecasting
- Voice Review Analysis
- Mobile Application

---

# 🎯 Project Outcomes

✔ Automated customer review analysis

✔ AI-powered sentiment classification

✔ Product rating visualization

✔ Interactive analytical dashboard

✔ Business decision support

✔ Reduced manual effort

✔ Fast review processing

✔ Improved customer insight

✔ Sales impact prediction

✔ Better product improvement strategy

---

# 📚 Learning Outcomes

During this project, we gained practical experience in:

- Python Development
- Flask Framework
- Web Scraping using Selenium
- Natural Language Processing
- VADER Sentiment Analysis
- Data Visualization
- REST-based Web Application Development
- Frontend Development
- Backend Integration
- Git & GitHub
- Software Development Lifecycle

---

# 🤝 Contributors

| Name | Role |
|------|------|
| Amar Das | Backend Development, Flask, NLP |
| Raj Kumar | AI/ML & Model Integration |
| Sudhanshu Singh | Frontend Development |
| Devdeep Singh | Testing & Documentation |
| Rishi Rikhi | Research & Data Collection |

---

# 📜 License

This project is developed for educational and academic purposes.

Copyright © 2026 FeedBackIQ Team

---

# ⭐ Support

If you found this project useful,

⭐ Star this repository.

---

<div align="center">

## Thank You ❤️

**FeedBackIQ — Transforming Customer Reviews into Business Intelligence**

</div>
