from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ----------------------------
# Paths
# ----------------------------
DATA_DIR = Path("data")
CSV_PATH = DATA_DIR / "transactions.csv"

OUTPUT_DIR = Path("outputs")
REPORT_PATH = OUTPUT_DIR / "report.txt"
CHART_PATH = OUTPUT_DIR / "spending_by_category.png"


# ----------------------------
# Helpers
# ----------------------------
def ensure_files_exist() -> None:
    """Create data/transactions.csv and outputs/ folder if missing."""
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    if not CSV_PATH.exists():
        df = pd.DataFrame(columns=["date", "description", "amount"])
        df.to_csv(CSV_PATH, index=False)


def load_df() -> pd.DataFrame:
    ensure_files_exist()
    df = pd.read_csv(CSV_PATH)

    # Make sure columns exist even if file is weird
    for col in ["date", "description", "amount"]:
        if col not in df.columns:
            df[col] = None

    # Clean types
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["description"] = df["description"].astype(str)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Drop bad rows
    df = df.dropna(subset=["date", "description", "amount"])
    return df


def save_df(df: pd.DataFrame) -> None:
    ensure_files_exist()
    # Save date back to string YYYY-MM-DD
    df2 = df.copy()
    df2["date"] = pd.to_datetime(df2["date"]).dt.strftime("%Y-%m-%d")
    df2.to_csv(CSV_PATH, index=False)


def categorize(description: str) -> str:
    d = description.lower()

    rules = {
        "Groceries": ["walmart", "grocery", "costco", "superstore", "sobeys", "freshco"],
        "Food": ["starbucks", "restaurant", "pizza", "mcdonald", "tim", "tims", "cafe"],
        "Transport": ["uber", "lyft", "bus", "train", "taxi", "gas", "petro", "shell", "esso"],
        "Subscription": ["netflix", "spotify", "prime", "apple", "disney"],
        "Bills": ["phone", "internet", "rent", "hydro", "electric", "water", "bill"],
        "Income": ["salary", "payroll", "bonus", "refund"],
    }

    for category, keywords in rules.items():
        if any(k in d for k in keywords):
            return category

    return "Other"


# ----------------------------
# Features
# ----------------------------
def add_transaction() -> None:
    df = load_df()

    date_str = input("Date (YYYY-MM-DD): ").strip()
    description = input("Description: ").strip()

    try:
        amount = float(input("Amount (negative=expense, positive=income): ").strip())
    except ValueError:
        print("❌ Amount must be a number.")
        return

    date_val = pd.to_datetime(date_str, errors="coerce")
    if pd.isna(date_val):
        print("❌ Invalid date. Use YYYY-MM-DD (example: 2026-03-04)")
        return

    df.loc[len(df)] = [date_val.date(), description, amount]
    save_df(df)
    print("✅ Transaction added.")


def view_transactions() -> None:
    df = load_df()
    if df.empty:
        print("No transactions yet.")
        return

    df_show = df.copy()
    df_show["date"] = df_show["date"].astype(str)
    print("\n=== Transactions (index shown on left) ===")
    print(df_show.to_string(index=True))


def delete_transaction() -> None:
    df = load_df()
    if df.empty:
        print("No transactions to delete.")
        return

    df_show = df.copy()
    df_show["date"] = df_show["date"].astype(str)
    print(df_show.to_string(index=True))

    try:
        idx = int(input("\nEnter index to delete: ").strip())
    except ValueError:
        print("❌ Please enter a valid number index.")
        return

    if idx not in df.index:
        print("❌ Invalid index.")
        return

    df = df.drop(idx).reset_index(drop=True)
    save_df(df)
    print("✅ Deleted.")


def summary_and_category_spend(df: pd.DataFrame):
    income = df.loc[df["amount"] > 0, "amount"].sum()
    expenses = df.loc[df["amount"] < 0, "amount"].sum()  # negative
    net = income + expenses

    df2 = df.copy()
    df2["category"] = df2["description"].apply(categorize)

    spending_abs = (
        df2[df2["amount"] < 0]
        .groupby("category")["amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
    )

    return income, expenses, net, spending_abs


def print_summary() -> None:
    df = load_df()
    if df.empty:
        print("No transactions to summarize.")
        return

    income, expenses, net, spending_abs = summary_and_category_spend(df)

    print("\n===== FINANCE SUMMARY =====")
    print(f"Total Income:   ${income:.2f}")
    print(f"Total Expenses: ${abs(expenses):.2f}")
    print(f"Net:            ${net:.2f}")

    print("\nSpending by Category:")
    if spending_abs.empty:
        print("(No expenses yet)")
    else:
        print(spending_abs)


def spending_chart(save_file: bool = True) -> None:
    df = load_df()
    if df.empty:
        print("No transactions yet.")
        return

    _, _, _, spending_abs = summary_and_category_spend(df)

    if spending_abs.empty:
        print("No expenses to chart yet.")
        return

    ax = spending_abs.plot(kind="bar")
    plt.title("Spending by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount ($)")
    plt.tight_layout()

    if save_file:
        ensure_files_exist()
        plt.savefig(CHART_PATH)
        print(f"✅ Saved chart -> {CHART_PATH}")

    plt.show()


def export_report() -> None:
    df = load_df()
    if df.empty:
        print("No transactions to export.")
        return

    income, expenses, net, spending_abs = summary_and_category_spend(df)

    ensure_files_exist()
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("===== FINANCE SUMMARY =====\n")
        f.write(f"Total Income:   ${income:.2f}\n")
        f.write(f"Total Expenses: ${abs(expenses):.2f}\n")
        f.write(f"Net:            ${net:.2f}\n\n")
        f.write("Spending by Category:\n")
        if spending_abs.empty:
            f.write("(No expenses yet)\n")
        else:
            f.write(spending_abs.to_string())
            f.write("\n")

    print(f"✅ Saved report -> {REPORT_PATH}")


# ----------------------------
# Menu
# ----------------------------
def menu() -> None:
    ensure_files_exist()

    while True:
        print("\n===== FINANCE TRACKER =====")
        print("1) Add transaction")
        print("2) View transactions")
        print("3) Summary")
        print("4) Delete transaction")
        print("5) Spending chart (and save)")
        print("6) Export report (txt)")
        print("7) Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            add_transaction()
        elif choice == "2":
            view_transactions()
        elif choice == "3":
            print_summary()
        elif choice == "4":
            delete_transaction()
        elif choice == "5":
            spending_chart(save_file=True)
        elif choice == "6":
            export_report()
        elif choice == "7":
            print("Bye!")
            break
        else:
            print("Invalid choice. Pick 1–7.")


if __name__ == "__main__":
    menu()