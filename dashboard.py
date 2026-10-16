import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

DATABASE_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "crypto_anomaly.db"
)

st.set_page_config(
    page_title="Crypto Anomaly Tracker",
    page_icon="📈",
    layout="wide",
)

st.title("Crypto Anomaly Tracker")
st.caption("Cryptocurrency prices and anomaly detection")
source_filter = st.selectbox(
    "Data source",
    options=["All sources", "CoinGecko", "Manual tests", "Unknown"],
)
source_values = {
    "CoinGecko": "coingecko",
    "Manual tests": "manual-test",
    "Unknown": "unknown",
}

selected_source = source_values.get(source_filter)

if st.button("Refresh data"):
    st.rerun()


def read_query(query, params=()):
    """Read data from the local SQLite database."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=params,
        )


if not DATABASE_PATH.exists():
    st.error("Database not found. Start the project pipeline first.")
    st.stop()


# Get the most recently saved observation for each coin.
latest_prices_query = """
    SELECT p.coin, p.price_usd, p.change_percent, p.timestamp_utc
    FROM price_observations AS p
    INNER JOIN (
        SELECT coin, MAX(id) AS latest_id
        FROM price_observations
        WHERE (? IS NULL OR source = ?)
        GROUP BY coin
    ) AS latest ON p.id = latest.latest_id
    ORDER BY p.coin
"""

latest_prices = read_query(
    latest_prices_query,
    (selected_source, selected_source),
)

# Load recent price history.
# Load price history for the selected source.
history_query = """
    SELECT timestamp_utc, coin, price_usd
    FROM price_observations
    WHERE (? IS NULL OR source = ?)
    ORDER BY id
"""

history = read_query(
    history_query,
    (selected_source, selected_source),
)

# Load recent anomalies for the selected source.
anomalies_query = """
    SELECT
        timestamp_utc,
        coin,
        previous_price_usd,
        new_price_usd,
        change_percent,
        threshold_percent
    FROM anomalies
    WHERE (? IS NULL OR source = ?)
    ORDER BY id DESC
    LIMIT 20
"""

anomalies = read_query(
    anomalies_query,
    (selected_source, selected_source),
)


st.subheader("Latest recorded prices")

if latest_prices.empty:
    if selected_source is None:
        st.info("No price observations yet. Start the producer and consumer.")
    else:
        st.info(f"No price observations found for {source_filter}.")
else:
    columns = st.columns(3)
    preferred_order = ["bitcoin", "ethereum", "solana"]

    for index, coin in enumerate(preferred_order):
        match = latest_prices[latest_prices["coin"] == coin]

        if match.empty:
            continue

        price = match.iloc[0]["price_usd"]
        change = match.iloc[0]["change_percent"]

        with columns[index]:
            st.metric(
                label=coin.capitalize(),
                value=f"${price:,.2f}",
                delta=(
                    f"{change:+.2f}%"
                    if pd.notna(change)
                    else "Baseline"
                ),
            )


st.divider()
st.subheader("Price history")

if history.empty:
    st.info("Price history will appear after observations are saved.")
else:
    history["timestamp_utc"] = pd.to_datetime(
        history["timestamp_utc"], utc=True
    ).dt.tz_convert("Africa/Lusaka")

    st.line_chart(
        history,
        x="timestamp_utc",
        y="price_usd",
        color="coin",
    )


st.divider()
st.subheader("Recent anomalies")

if anomalies.empty:
    if selected_source is None:
        st.success("No anomalies have been recorded.")
    else:
        st.success(f"No anomalies have been recorded for {source_filter}.")
else:
    anomalies["timestamp_utc"] = pd.to_datetime(
        anomalies["timestamp_utc"], utc=True
    ).dt.tz_convert("Africa/Lusaka")

    anomalies = anomalies.rename(columns={
        "timestamp_utc": "Time (CAT)",
        "coin": "Coin",
        "previous_price_usd": "Previous price ($)",
        "new_price_usd": "New price ($)",
        "change_percent": "Change (%)",
        "threshold_percent": "Threshold (%)",
    })

    st.dataframe(
        anomalies,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Previous price ($)": st.column_config.NumberColumn(
                format="$%.2f"
            ),
            "New price ($)": st.column_config.NumberColumn(
                format="$%.2f"
            ),
            "Change (%)": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "Threshold (%)": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
        },
    )


st.caption(
    "Data comes from the local SQLite database. "
    "Prices update when the consumer saves new observations; "
    "click Refresh data to reload the dashboard."
)

st_autorefresh(
    interval=15_000,
    key="dashboard_refresh",
)
