import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = Path("data/transactions.csv")


def load_data():
    if not DATA_PATH.exists():
        df = pd.DataFrame(columns=["date", "description", "amount"])
        df.to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)


def save_data(df):
    df.to_csv(DATA_PATH, index=False)


st.title("💰 Finance Tracker Dashboard")

df = load_data()

# ---- Summary ----
income = df[df["amount"] > 0]["amount"].sum()
expenses = df[df["amount"] < 0]["amount"].sum()
net = income + expenses

col1, col2, col3 = st.columns(3)

col1.metric("Income", f"${income:.2f}")
col2.metric("Expenses", f"${abs(expenses):.2f}")
col3.metric("Net", f"${net:.2f}")

st.divider()

# ---- Add Transaction ----
st.subheader("Add Transaction")

date = st.date_input("Date")
desc = st.text_input("Description")
amount = st.number_input("Amount", step=1.0)

if st.button("Add"):
    new_row = pd.DataFrame([[date, desc, amount]], columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    st.success("Transaction added!")
    st.rerun()

st.divider()

# ---- Transactions Table ----
st.subheader("Transactions")

st.dataframe(df)

st.divider()

# ---- Spending Chart ----
st.subheader("Spending Chart")

expenses_df = df[df["amount"] < 0]

if not expenses_df.empty:

    expenses_df["category"] = expenses_df["description"]

    spending = expenses_df.groupby("category")["amount"].sum().abs()

    fig, ax = plt.subplots()

    spending.plot(kind="bar", ax=ax)

    ax.set_title("Spending by Category")
    ax.set_ylabel("Amount")

    st.pyplot(fig)

else:
    st.write("No expenses yet.")