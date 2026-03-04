import os
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = Path("data") / "transactions.csv"
OUTPUT_DIR = Path("outputs")


def categorize(description: str) -> str:
    d = description.lower()

    rules = {
        "Groceries": ["walmart", "grocery", "costco", "superstore", "sobeys"],
        "Food": ["starbucks", "restaurant", "pizza", "mcdonald", "tim", "tims", "cafe"],
        "Transport": ["uber", "lyft", "bus", "train", "taxi", "gas", "petro", "shell", "esso"],
        "Subscription": ["netflix", "spotify", "prime", "apple", "disney"],
        "Bills": ["phone", "internet", "rent", "hydro", "electric", "water"],
        "Income": ["salary", "payroll", "bonus", "refund"],
    }

    for category, keywords in rules.items():
        if any(k in d for k in keywords):
            return category

    return "Other"


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Could not find file: {path.resolve()}")

    df = pd.read_csv(path)

    required_cols = {"date", "description", "amount"}
    if not required_cols.issubset(set(df.columns)):
        raise ValueError(f"CSV must contain columns: {required_cols}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["date", "description", "amount"])

    return df


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    df = load_data(DATA_PATH)
    df["category"] = df["description"].apply(categorize)

    income = df.loc[df["amount"] > 0, "amount"].sum()
    expenses = df.loc[df["amount"] < 0, "amount"].sum()  # negative
    net = income + expenses

    # Spending by category (expenses only)
    spending_abs = (
        df[df["amount"] < 0]
        .groupby("category")["amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
    )

    print("\n===== FINANCE SUMMARY =====")
    print(f"Total Income:   ${income:.2f}")
    print(f"Total Expenses: ${abs(expenses):.2f}")
    print(f"Net:            ${net:.2f}")

    print("\nSpending by Category:")
    print(spending_abs)

    # Save report
    report_path = OUTPUT_DIR / "report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("===== FINANCE SUMMARY =====\n")
        f.write(f"Total Income:   ${income:.2f}\n")
        f.write(f"Total Expenses: ${abs(expenses):.2f}\n")
        f.write(f"Net:            ${net:.2f}\n\n")
        f.write("Spending by Category:\n")
        f.write(spending_abs.to_string())
        f.write("\n")

    # Save chart
    if not spending_abs.empty:
        ax = spending_abs.plot(kind="bar")
        plt.title("Spending by Category")
        plt.xlabel("Category")
        plt.ylabel("Amount ($)")
        plt.tight_layout()

        chart_path = OUTPUT_DIR / "spending_by_category.png"
        plt.savefig(chart_path)
        plt.show()

    print(f"\nSaved report -> {report_path}")
    print(f"Saved chart  -> {(OUTPUT_DIR / 'spending_by_category.png')}")


if __name__ == "__main__":
    main()