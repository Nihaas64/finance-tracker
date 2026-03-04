# Finance Tracker (Python)

A simple finance tracker built in Python that reads transactions from a CSV file, categorizes spending automatically, and generates financial summaries and charts.

## Features
- Reads transactions from `data/transactions.csv`
- Automatically categorizes spending
- Calculates total income and expenses
- Generates a spending chart
- Exports a financial report

## Technologies Used
- Python
- Pandas
- Matplotlib

## Project Structure

finance-tracker/
│
├── main.py
├── requirements.txt
├── README.md
│
├── data/
│   └── transactions.csv
│
└── outputs/
    ├── report.txt
    └── spending_by_category.png

## How to Run

1. Install required libraries

pip install -r requirements.txt

2. Run the program

python main.py

## Example CSV Format

date,description,amount  
2026-03-01,Walmart Groceries,-54.23  
2026-03-02,Salary,1500.00  

Expenses should be negative numbers and income should be positive.

## Future Improvements

- Add transactions through the terminal
- Monthly spending reports
- Interactive dashboard