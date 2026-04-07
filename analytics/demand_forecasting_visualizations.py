from pathlib import Path
from datetime import datetime
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import STL
from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]

EXPORT_DIR = BASE_DIR / "data" / "exports"
REPORT_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORT_DIR / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

product_demand = pd.read_parquet(EXPORT_DIR / "top_product_demand_timeseries.parquet")
department_demand = pd.read_parquet(EXPORT_DIR / "department_demand_timeseries.parquet")

reorder_intervals = pd.read_csv(
    EXPORT_DIR / "reorder_intervals.csv"
)

customer_reorder = pd.read_csv(
    EXPORT_DIR / "customer_reorder_behavior.csv"
)

customer_lifetime_curve = pd.read_csv(
    EXPORT_DIR / "customer_lifetime_curve.csv"
)

customer_reorder_cohorts = pd.read_csv(
    EXPORT_DIR / "customer_reorder_cohorts.csv"
)

def plot_product_demand_trends():

    df = product_demand.copy()

    plt.figure(figsize=(10,6))

    for product in df["product_name"].unique():
        sub = df[df["product_name"] == product]
        plt.plot(
            sub["relative_week_index"],
            sub["units_sold"],
            label=product
        )

    plt.xlabel("Relative Week Index")
    plt.ylabel("Units Sold")
    plt.title("Product Demand Trends")

    plt.legend()

    path = FIGURES_DIR / "product_demand_trends.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def plot_department_demand_trends():

    df = department_demand.copy()

    plt.figure(figsize=(10,6))

    for dep in df["department"].unique():
        sub = df[df["department"] == dep]

        plt.plot(
            sub["relative_week_index"],
            sub["units_sold"],
            label=dep
        )

    plt.xlabel("Relative Week Index")
    plt.ylabel("Units Sold")
    plt.title("Department Demand Trends")

    plt.legend()

    path = FIGURES_DIR / "department_demand_trends.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def plot_top_products():

    df = product_demand.groupby(
        ["product_name"]
    )["units_sold"].sum().sort_values(ascending=False)

    df = df.head(10)

    plt.figure(figsize=(10,6))

    plt.barh(
        df.index[::-1],
        df.values[::-1]
    )

    plt.xlabel("Units Sold")
    plt.title("Top Products by Total Demand")

    path = FIGURES_DIR / "top_products_total_demand.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def plot_top_departments():

    df = department_demand.groupby(
        ["department"]
    )["units_sold"].sum().sort_values(ascending=False)

    plt.figure(figsize=(10,6))

    plt.barh(
        df.index[::-1],
        df.values[::-1]
    )

    plt.xlabel("Units Sold")
    plt.title("Top Departments by Demand")

    path = FIGURES_DIR / "top_departments_total_demand.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def compute_moving_average_forecast(df, window=4):

    df = df.sort_values("relative_week_index")

    df["moving_avg"] = (
        df["units_sold"]
        .rolling(window=window)
        .mean()
    )

    return df

def build_product_forecast_dataset():

    forecasts = []

    for product in product_demand["product_name"].unique():

        sub = product_demand[
            product_demand["product_name"] == product
        ].copy()

        sub = compute_moving_average_forecast(sub)

        sub["product_name"] = product

        forecasts.append(sub)

    return pd.concat(forecasts)

def plot_product_forecast():

    df = build_product_forecast_dataset()

    plt.figure(figsize=(10,6))

    for product in df["product_name"].unique():

        sub = df[df["product_name"] == product]

        plt.plot(
            sub["relative_week_index"],
            sub["units_sold"],
            label=f"{product} actual"
        )

        plt.plot(
            sub["relative_week_index"],
            sub["moving_avg"],
            linestyle="--",
            label=f"{product} MA forecast"
        )

    plt.xlabel("Relative Week")
    plt.ylabel("Units Sold")
    plt.title("Moving Average Demand Forecast")

    plt.legend()

    path = FIGURES_DIR / "moving_average_forecast.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def plot_weekly_demand_distribution():

    df = department_demand.copy()

    weekly = df.groupby("relative_week_index")["units_sold"].sum()

    plt.figure(figsize=(10,6))

    plt.plot(weekly.index, weekly.values)

    plt.xlabel("Relative Week")
    plt.ylabel("Units Sold")

    plt.title("Weekly Demand Evolution")

    path = FIGURES_DIR / "weekly_demand_evolution.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def detect_demand_anomalies():

    df = department_demand.copy()

    weekly = df.groupby("relative_week_index")["units_sold"].sum()

    mean = weekly.mean()
    std = weekly.std()

    z_scores = (weekly - mean) / std

    anomalies = weekly[abs(z_scores) > 3]

    return weekly, anomalies

def plot_demand_anomalies():

    weekly, anomalies = detect_demand_anomalies()

    plt.figure(figsize=(10,6))

    plt.plot(weekly.index, weekly.values, label="Demand")

    plt.scatter(
        anomalies.index,
        anomalies.values,
        color="red",
        label="Anomaly"
    )

    plt.title("Demand Anomaly Detection")

    plt.xlabel("Relative Week")
    plt.ylabel("Units Sold")

    plt.legend()

    path = FIGURES_DIR / "demand_anomalies.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def compute_product_peak_weeks() -> pd.DataFrame:
    df = product_demand.copy()

    peak_df = (
        df.sort_values(
            ["product_id", "units_sold", "relative_week_index"],
            ascending=[True, False, True]
        )
        .groupby("product_id", as_index=False)
        .first()[["product_id", "product_name", "department", "relative_week_index", "units_sold"]]
        .rename(columns={
            "relative_week_index": "peak_relative_week",
            "units_sold": "peak_units_sold"
        })
    )

    return peak_df

def compute_department_peak_weeks() -> pd.DataFrame:
    df = department_demand.copy()

    peak_df = (
        df.sort_values(
            ["department", "units_sold", "relative_week_index"],
            ascending=[True, False, True]
        )
        .groupby("department", as_index=False)
        .first()[["department", "relative_week_index", "units_sold"]]
        .rename(columns={
            "relative_week_index": "peak_relative_week",
            "units_sold": "peak_units_sold"
        })
    )

    return peak_df

def compute_product_peak_weeks(exclude_week_zero: bool = True) -> pd.DataFrame:
    df = product_demand.copy()

    required_cols = {
        "product_id",
        "product_name",
        "department",
        "relative_week_index",
        "units_sold",
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in product_demand: {sorted(missing)}")

    df = df.dropna(subset=["product_id", "product_name", "relative_week_index", "units_sold"]).copy()
    df["relative_week_index"] = pd.to_numeric(df["relative_week_index"], errors="coerce")
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
    df = df.dropna(subset=["relative_week_index", "units_sold"]).copy()

    if exclude_week_zero:
        df = df[df["relative_week_index"] > 0].copy()

    if df.empty:
        return pd.DataFrame(
            columns=[
                "product_id",
                "product_name",
                "department",
                "peak_relative_week",
                "peak_units_sold",
            ]
        )

    peak_df = (
        df.sort_values(
            by=["product_id", "units_sold", "relative_week_index"],
            ascending=[True, False, True],
        )
        .groupby("product_id", as_index=False)
        .first()
        .loc[:, ["product_id", "product_name", "department", "relative_week_index", "units_sold"]]
        .rename(
            columns={
                "relative_week_index": "peak_relative_week",
                "units_sold": "peak_units_sold",
            }
        )
    )

    peak_df["peak_relative_week"] = peak_df["peak_relative_week"].astype(int)
    peak_df["peak_units_sold"] = peak_df["peak_units_sold"].astype(int)

    return peak_df


def compute_department_peak_weeks(exclude_week_zero: bool = True) -> pd.DataFrame:
    df = department_demand.copy()

    required_cols = {
        "department",
        "relative_week_index",
        "units_sold",
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in department_demand: {sorted(missing)}")

    df = df.dropna(subset=["department", "relative_week_index", "units_sold"]).copy()
    df["relative_week_index"] = pd.to_numeric(df["relative_week_index"], errors="coerce")
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
    df = df.dropna(subset=["relative_week_index", "units_sold"]).copy()

    if exclude_week_zero:
        df = df[df["relative_week_index"] > 0].copy()

    if df.empty:
        return pd.DataFrame(
            columns=[
                "department",
                "peak_relative_week",
                "peak_units_sold",
            ]
        )

    peak_df = (
        df.sort_values(
            by=["department", "units_sold", "relative_week_index"],
            ascending=[True, False, True],
        )
        .groupby("department", as_index=False)
        .first()
        .loc[:, ["department", "relative_week_index", "units_sold"]]
        .rename(
            columns={
                "relative_week_index": "peak_relative_week",
                "units_sold": "peak_units_sold",
            }
        )
    )

    peak_df["peak_relative_week"] = peak_df["peak_relative_week"].astype(int)
    peak_df["peak_units_sold"] = peak_df["peak_units_sold"].astype(int)

    return peak_df

def plot_product_peak_weeks() -> Path | None:
    df = compute_product_peak_weeks(exclude_week_zero=True)

    if df.empty:
        print("No product peak-week data available after excluding week 0.")
        return None

    df = df.sort_values(["peak_relative_week", "peak_units_sold"], ascending=[True, False]).copy()

    plt.figure(figsize=(11, 6))
    bars = plt.barh(df["product_name"], df["peak_relative_week"])

    max_week = int(df["peak_relative_week"].max()) if not df.empty else 1
    label_offset = max(0.3, max_week * 0.01)

    for bar, week, units in zip(bars, df["peak_relative_week"], df["peak_units_sold"]):
        plt.text(
            bar.get_width() + label_offset,
            bar.get_y() + (bar.get_height() / 2),
            f"W{int(week)} · {int(units):,}",
            va="center",
            fontsize=9,
        )

    plt.xlabel("Peak Relative Week")
    plt.title("Peak Relative Week by Product (Excluding Week 0)")
    plt.xlim(0, max_week + max(2, int(max_week * 0.12)))

    path = FIGURES_DIR / "product_peak_weeks.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path


def plot_department_peak_weeks() -> Path | None:
    df = compute_department_peak_weeks(exclude_week_zero=True)

    if df.empty:
        print("No department peak-week data available after excluding week 0.")
        return None

    df = df.sort_values(["peak_relative_week", "peak_units_sold"], ascending=[True, False]).copy()

    plt.figure(figsize=(11, 7))
    bars = plt.barh(df["department"], df["peak_relative_week"])

    max_week = int(df["peak_relative_week"].max()) if not df.empty else 1
    label_offset = max(0.3, max_week * 0.01)

    for bar, week, units in zip(bars, df["peak_relative_week"], df["peak_units_sold"]):
        plt.text(
            bar.get_width() + label_offset,
            bar.get_y() + (bar.get_height() / 2),
            f"W{int(week)} · {int(units):,}",
            va="center",
            fontsize=9,
        )

    plt.xlabel("Peak Relative Week")
    plt.title("Peak Relative Week by Department (Excluding Week 0)")
    plt.xlim(0, max_week + max(2, int(max_week * 0.12)))

    path = FIGURES_DIR / "department_peak_weeks.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def plot_department_peak_weeks():

    df = compute_department_peak_weeks(exclude_week_zero=True)
    df = df.sort_values("peak_relative_week", ascending=True)

    if df.empty:
        return None

    plt.figure(figsize=(10, 6))
    bars = plt.barh(df["department"], df["peak_relative_week"])

    for bar, week, units in zip(bars, df["peak_relative_week"], df["peak_units_sold"]):
        plt.text(
            bar.get_width() + 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"W{int(week)} · {int(units):,}",
            va="center",
            fontsize=9
        )

    plt.xlabel("Peak Relative Week")
    plt.title("Peak Relative Week by Department (Excluding Week 0)")

    path = FIGURES_DIR / "department_peak_weeks.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def plot_weekly_demand_pattern():

    df = department_demand.copy()

    weekly = (
        df.groupby("relative_week_index")["units_sold"]
        .sum()
        .reset_index()
    )

    weekly = weekly[weekly["relative_week_index"] > 0]

    plt.figure(figsize=(10,6))

    plt.plot(
        weekly["relative_week_index"],
        weekly["units_sold"],
        marker="o"
    )

    for x, y in zip(weekly["relative_week_index"], weekly["units_sold"]):
        if x % 4 == 0:
            plt.axvline(x=x, linestyle="--", alpha=0.2)

    plt.xlabel("Relative Week")
    plt.ylabel("Units Sold")
    plt.title("Weekly Demand Pattern")

    path = FIGURES_DIR / "weekly_demand_pattern.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def plot_replenishment_cycle():

    df = department_demand.copy()

    df = df[df["relative_week_index"] > 0]

    df["cycle_week"] = df["relative_week_index"] % 4

    cycle = (
        df.groupby("cycle_week")["units_sold"]
        .sum()
        .reset_index()
    )

    plt.figure(figsize=(8,5))

    plt.bar(
        cycle["cycle_week"],
        cycle["units_sold"]
    )

    plt.xlabel("Week in 4-Week Cycle")
    plt.ylabel("Units Sold")
    plt.title("4-Week Replenishment Cycle Pattern")

    path = FIGURES_DIR / "replenishment_cycle_pattern.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def plot_product_week_heatmap():

    df = product_demand.copy()

    pivot = df.pivot_table(
        index="product_name",
        columns="relative_week_index",
        values="units_sold",
        aggfunc="sum"
    )

    pivot = pivot.fillna(0)

    plt.figure(figsize=(12,6))

    plt.imshow(pivot, aspect="auto")

    plt.colorbar(label="Units Sold")

    plt.xlabel("Relative Week")
    plt.ylabel("Product")

    plt.title("Product Demand Heatmap")

    path = FIGURES_DIR / "product_demand_heatmap.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def plot_demand_acf():

    df = department_demand.copy()

    weekly = (
        df.groupby("relative_week_index")["units_sold"]
        .sum()
        .sort_index()
    )

    weekly = weekly[weekly.index > 0]

    plt.figure(figsize=(10,6))

    plot_acf(
        weekly,
        lags=20,
        alpha=0.05
    )

    plt.title("Demand Autocorrelation (ACF)")

    path = FIGURES_DIR / "demand_acf.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def plot_arima_forecast():

    df = department_demand.copy()

    weekly = (
        df.groupby("relative_week_index")["units_sold"]
        .sum()
        .sort_index()
    )

    # Exclure la semaine 0 si tu veux rester cohérent avec le reste du rapport
    weekly = weekly[weekly.index > 0]

    # Garder l'index relatif original pour l'affichage
    original_index = weekly.index.to_list()

    # Remplacer l'index par un RangeIndex supporté par statsmodels
    weekly_reset = pd.Series(
        weekly.values,
        index=pd.RangeIndex(start=0, stop=len(weekly), step=1),
        name="units_sold"
    )

    model = ARIMA(weekly_reset, order=(1, 1, 1))
    fitted = model.fit()

    forecast_steps = 12
    forecast = fitted.forecast(steps=forecast_steps)

    # Reconstruire un axe futur en semaines relatives
    last_relative_week = int(max(original_index))
    future_relative_index = list(
        range(last_relative_week + 1, last_relative_week + 1 + forecast_steps)
    )

    plt.figure(figsize=(10, 6))

    plt.plot(
        original_index,
        weekly.values,
        label="Actual"
    )

    plt.plot(
        future_relative_index,
        forecast.values,
        linestyle="--",
        label="ARIMA forecast"
    )

    plt.xlabel("Relative Week")
    plt.ylabel("Units Sold")
    plt.title("ARIMA Demand Forecast")
    plt.legend()

    path = FIGURES_DIR / "arima_forecast.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def build_product_series(product_name: str, exclude_week_zero: bool = True) -> pd.Series:
    df = product_demand.copy()

    required_cols = {"product_name", "relative_week_index", "units_sold"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in product_demand: {sorted(missing)}")

    df = df[df["product_name"] == product_name].copy()

    df["relative_week_index"] = pd.to_numeric(df["relative_week_index"], errors="coerce")
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
    df = df.dropna(subset=["relative_week_index", "units_sold"]).copy()

    if exclude_week_zero:
        df = df[df["relative_week_index"] > 0].copy()

    weekly = (
        df.groupby("relative_week_index")["units_sold"]
        .sum()
        .sort_index()
    )

    return weekly

def plot_product_series(product_name: str = "Banana") -> Path | None:
    weekly = build_product_series(product_name=product_name, exclude_week_zero=True)

    if weekly.empty or len(weekly) < 8:
        print(f"Not enough data for product series: {product_name}")
        return None

    plt.figure(figsize=(10, 6))
    plt.plot(weekly.index, weekly.values, marker="o")

    plt.xlabel("Relative Week")
    plt.ylabel("Units Sold")
    plt.title(f"Weekly Demand Series - {product_name}")

    path = FIGURES_DIR / f"product_series_{product_name.lower().replace(' ', '_')}.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def build_normalized_department_series(exclude_week_zero: bool = True) -> pd.Series:
    df = department_demand.copy()

    required_cols = {"relative_week_index", "units_sold", "orders_count"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in department_demand: {sorted(missing)}")

    df["relative_week_index"] = pd.to_numeric(df["relative_week_index"], errors="coerce")
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
    df["orders_count"] = pd.to_numeric(df["orders_count"], errors="coerce")
    df = df.dropna(subset=["relative_week_index", "units_sold", "orders_count"]).copy()

    if exclude_week_zero:
        df = df[df["relative_week_index"] > 0].copy()

    weekly = (
        df.groupby("relative_week_index")[["units_sold", "orders_count"]]
        .sum()
        .reset_index()
    )

    weekly = weekly[weekly["orders_count"] > 0].copy()
    weekly["units_per_order"] = weekly["units_sold"] / weekly["orders_count"]

    series = weekly.set_index("relative_week_index")["units_per_order"].sort_index()

    return series

def plot_normalized_department_series() -> Path | None:
    weekly = build_normalized_department_series(exclude_week_zero=True)

    if weekly.empty or len(weekly) < 8:
        print("Not enough data for normalized department series.")
        return None

    plt.figure(figsize=(10, 6))
    plt.plot(weekly.index, weekly.values, marker="o")

    plt.xlabel("Relative Week")
    plt.ylabel("Units per Order")
    plt.title("Normalized Department Demand Series")

    path = FIGURES_DIR / "normalized_department_series.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def plot_arima_product_forecast(product_name: str = "Banana", order: tuple = (1, 1, 1)) -> Path | None:
    weekly = build_product_series(product_name=product_name, exclude_week_zero=True)

    if weekly.empty or len(weekly) < 12:
        print(f"Not enough data for ARIMA product forecast: {product_name}")
        return None

    original_index = weekly.index.to_list()

    weekly_reset = pd.Series(
        weekly.values,
        index=pd.RangeIndex(start=0, stop=len(weekly), step=1),
        name="units_sold"
    )

    model = ARIMA(weekly_reset, order=order)
    fitted = model.fit()

    forecast_steps = 12
    forecast = fitted.forecast(steps=forecast_steps)

    last_relative_week = int(max(original_index))
    future_relative_index = list(
        range(last_relative_week + 1, last_relative_week + 1 + forecast_steps)
    )

    plt.figure(figsize=(10, 6))

    plt.plot(
        original_index,
        weekly.values,
        label="Actual"
    )

    plt.plot(
        future_relative_index,
        forecast.values,
        linestyle="--",
        label="ARIMA forecast"
    )

    plt.xlabel("Relative Week")
    plt.ylabel("Units Sold")
    plt.title(f"ARIMA Forecast - {product_name}")
    plt.legend()

    path = FIGURES_DIR / f"arima_forecast_{product_name.lower().replace(' ', '_')}.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def plot_arima_normalized_department_forecast(order: tuple = (1, 1, 1)) -> Path | None:
    weekly = build_normalized_department_series(exclude_week_zero=True)

    if weekly.empty or len(weekly) < 12:
        print("Not enough data for ARIMA normalized department forecast.")
        return None

    original_index = weekly.index.to_list()

    weekly_reset = pd.Series(
        weekly.values,
        index=pd.RangeIndex(start=0, stop=len(weekly), step=1),
        name="units_per_order"
    )

    model = ARIMA(weekly_reset, order=order)
    fitted = model.fit()

    forecast_steps = 12
    forecast = fitted.forecast(steps=forecast_steps)

    last_relative_week = int(max(original_index))
    future_relative_index = list(
        range(last_relative_week + 1, last_relative_week + 1 + forecast_steps)
    )

    plt.figure(figsize=(10, 6))

    plt.plot(
        original_index,
        weekly.values,
        label="Actual"
    )

    plt.plot(
        future_relative_index,
        forecast.values,
        linestyle="--",
        label="ARIMA forecast"
    )

    plt.xlabel("Relative Week")
    plt.ylabel("Units per Order")
    plt.title("ARIMA Forecast - Normalized Department Demand")
    plt.legend()

    path = FIGURES_DIR / "arima_forecast_normalized_department.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def plot_stl_decomposition(period: int = 4) -> Path | None:

    series = build_normalized_department_series(exclude_week_zero=True)

    if len(series) < period * 2:
        print("Not enough data for STL decomposition")
        return None

    stl = STL(series, period=period)
    result = stl.fit()

    fig = result.plot()

    fig.set_size_inches(10, 8)

    path = FIGURES_DIR / "stl_decomposition.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

    return path

def plot_reorder_interval_distribution():

    df = reorder_intervals.copy()

    df["days_since_prior_order"] = pd.to_numeric(
        df["days_since_prior_order"],
        errors="coerce"
    )

    df = df.dropna()

    plt.figure(figsize=(10,6))

    plt.hist(
        df["days_since_prior_order"],
        bins=30
    )

    plt.xlabel("Days Since Prior Order")
    plt.ylabel("Frequency")

    plt.title("Reorder Interval Distribution")

    path = FIGURES_DIR / "reorder_interval_distribution.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def build_customer_reorder_segments(customer_reorder: pd.DataFrame) -> pd.DataFrame:
    df = customer_reorder.copy()

    required_cols = {"user_id", "avg_reorder_days", "total_orders"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in customer_reorder: {sorted(missing)}")

    df["avg_reorder_days"] = pd.to_numeric(df["avg_reorder_days"], errors="coerce")
    df["total_orders"] = pd.to_numeric(df["total_orders"], errors="coerce")
    df = df.dropna(subset=["avg_reorder_days", "total_orders"]).copy()

    def assign_segment(x: float) -> str:
        if x <= 8:
            return "Weekly Shoppers"
        elif x <= 16:
            return "Bi-Weekly Shoppers"
        elif x < 30:
            return "Monthly Shoppers"
        else:
            return "Long-Interval Shoppers"

    df["reorder_segment"] = df["avg_reorder_days"].apply(assign_segment)

    segment_summary = (
        df.groupby("reorder_segment")
        .agg(
            customers=("user_id", "count"),
            avg_reorder_days=("avg_reorder_days", "mean"),
            avg_total_orders=("total_orders", "mean"),
        )
        .reset_index()
    )

    total_customers = segment_summary["customers"].sum()
    segment_summary["customer_share_pct"] = (
        segment_summary["customers"] / total_customers * 100
    ).round(1)

    order_map = {
        "Weekly Shoppers": 0,
        "Bi-Weekly Shoppers": 1,
        "Monthly Shoppers": 2,
        "Long-Interval Shoppers": 3,
    }
    segment_summary["sort_order"] = segment_summary["reorder_segment"].map(order_map)
    segment_summary = segment_summary.sort_values("sort_order").drop(columns="sort_order")

    return segment_summary

def plot_customer_reorder_segmentation(customer_reorder: pd.DataFrame) -> Path | None:
    segment_summary = build_customer_reorder_segments(customer_reorder)

    if segment_summary.empty:
        print("No customer reorder segmentation data available.")
        return None

    plt.figure(figsize=(10, 6))
    bars = plt.barh(
        segment_summary["reorder_segment"],
        segment_summary["customers"]
    )

    for bar, pct, avg_days in zip(
        bars,
        segment_summary["customer_share_pct"],
        segment_summary["avg_reorder_days"]
    ):
        plt.text(
            bar.get_width() * 1.01,
            bar.get_y() + bar.get_height() / 2,
            f"{pct:.1f}% · avg {avg_days:.1f}d",
            va="center",
            fontsize=9
        )

    plt.xlabel("Customers")
    plt.title("Customer Reorder Segmentation")

    path = FIGURES_DIR / "customer_reorder_segmentation.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def plot_customer_lifetime_ordering_curve(customer_lifetime_curve: pd.DataFrame) -> Path | None:
    df = customer_lifetime_curve.copy()

    required_cols = {"relative_week_index", "active_customers"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in customer_lifetime_curve: {sorted(missing)}")

    df["relative_week_index"] = pd.to_numeric(df["relative_week_index"], errors="coerce")
    df["active_customers"] = pd.to_numeric(df["active_customers"], errors="coerce")
    df = df.dropna(subset=["relative_week_index", "active_customers"]).copy()
    df = df.sort_values("relative_week_index")

    if df.empty:
        print("No customer lifetime curve data available.")
        return None

    plt.figure(figsize=(10, 6))
    plt.plot(
        df["relative_week_index"],
        df["active_customers"],
        marker="o"
    )

    plt.xlabel("Relative Week")
    plt.ylabel("Active Customers")
    plt.title("Customer Lifetime Ordering Curve")

    path = FIGURES_DIR / "customer_lifetime_ordering_curve.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def plot_reorder_interval_distribution_capped(reorder_intervals: pd.DataFrame) -> Path | None:
    df = reorder_intervals.copy()

    if "days_since_prior_order" not in df.columns:
        raise ValueError("Missing column: days_since_prior_order")

    df["days_since_prior_order"] = pd.to_numeric(
        df["days_since_prior_order"],
        errors="coerce"
    )
    df = df.dropna(subset=["days_since_prior_order"]).copy()

    if df.empty:
        print("No reorder interval data available.")
        return None

    plt.figure(figsize=(10, 6))

    plt.hist(
        df["days_since_prior_order"],
        bins=30
    )

    plt.axvline(
        x=30,
        linestyle="--",
        linewidth=2
    )

    ymax = plt.gca().get_ylim()[1]

    plt.text(
        30.2,
        ymax * 0.92,
        "30-day cap\n(values above 30 are truncated)",
        va="top",
        fontsize=9
    )

    plt.xlabel("Days Since Prior Order")
    plt.ylabel("Frequency")
    plt.title("Reorder Interval Distribution (with 30-Day Cap)")

    path = FIGURES_DIR / "reorder_interval_distribution_capped.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def plot_reorder_interval_cdf(reorder_intervals: pd.DataFrame) -> Path | None:
    df = reorder_intervals.copy()

    if "days_since_prior_order" not in df.columns:
        raise ValueError("Missing column: days_since_prior_order")

    df["days_since_prior_order"] = pd.to_numeric(
        df["days_since_prior_order"],
        errors="coerce"
    )
    df = df.dropna(subset=["days_since_prior_order"]).copy()

    if df.empty:
        print("No reorder interval data available.")
        return None

    values = df["days_since_prior_order"].sort_values().reset_index(drop=True)
    cdf = (values.index + 1) / len(values)

    plt.figure(figsize=(10, 6))
    plt.plot(values, cdf)

    plt.axvline(
        x=30,
        linestyle="--",
        linewidth=2
    )

    plt.text(
        30.2,
        0.9,
        "30-day cap",
        va="top",
        fontsize=9
    )

    plt.xlabel("Days Since Prior Order")
    plt.ylabel("Cumulative Share")
    plt.title("Cumulative Reorder Interval Distribution")

    path = FIGURES_DIR / "reorder_interval_cdf.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def plot_reorder_survival_curve(reorder_intervals):

    import numpy as np

    df = reorder_intervals.copy()

    days = np.sort(df["days_since_prior_order"].dropna())

    survival = 1 - np.arange(len(days)) / len(days)

    fig, ax = plt.subplots(figsize=(10,6))

    ax.step(days, survival)

    ax.axvline(30, linestyle="--")

    ax.set_title("Reorder Survival Curve")
    ax.set_xlabel("Days Since Prior Order")
    ax.set_ylabel("Probability of Reordering Later")

    fig.tight_layout()

    output = FIGURES_DIR / "reorder_survival_curve.png"
    fig.savefig(output, dpi=150)
    plt.close()

    return output

def plot_customer_reorder_cohorts(customer_reorder_cohorts: pd.DataFrame) -> Path | None:
    df = customer_reorder_cohorts.copy()

    required_cols = {"cohort_week", "cohort_age", "active_customers"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in customer_reorder_cohorts: {sorted(missing)}")

    df["cohort_week"] = pd.to_numeric(df["cohort_week"], errors="coerce")
    df["cohort_age"] = pd.to_numeric(df["cohort_age"], errors="coerce")
    df["active_customers"] = pd.to_numeric(df["active_customers"], errors="coerce")
    df = df.dropna(subset=["cohort_week", "cohort_age", "active_customers"]).copy()

    if df.empty:
        print("No customer reorder cohort data available.")
        return None

    cohort_sizes = (
        df[df["cohort_age"] == 0][["cohort_week", "active_customers"]]
        .rename(columns={"active_customers": "cohort_size"})
    )

    df = df.merge(cohort_sizes, on="cohort_week", how="left")
    df["retention_rate"] = df["active_customers"] / df["cohort_size"]

    pivot = df.pivot_table(
        index="cohort_week",
        columns="cohort_age",
        values="retention_rate",
        aggfunc="mean"
    ).fillna(0)

    plt.figure(figsize=(12, 7))
    plt.imshow(pivot, aspect="auto")
    plt.colorbar(label="Retention Rate")

    plt.xlabel("Weeks Since First Observed Order")
    plt.ylabel("Cohort Start Week")
    plt.title("Customer Reorder Cohorts")

    path = FIGURES_DIR / "customer_reorder_cohorts.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def plot_product_demand_seasonality_index(period: int = 4) -> Path | None:
    df = product_demand.copy()

    required_cols = {"product_name", "relative_week_index", "units_sold"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in product_demand: {sorted(missing)}")

    df["relative_week_index"] = pd.to_numeric(df["relative_week_index"], errors="coerce")
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
    df = df.dropna(subset=["product_name", "relative_week_index", "units_sold"]).copy()
    df = df[df["relative_week_index"] > 0].copy()

    if df.empty:
        print("No product demand data available for seasonality index.")
        return None

    df["cycle_position"] = df["relative_week_index"] % period

    baseline = (
        df.groupby("product_name")["units_sold"]
        .mean()
        .reset_index(name="avg_units")
    )

    cycle = (
        df.groupby(["product_name", "cycle_position"])["units_sold"]
        .mean()
        .reset_index(name="cycle_avg_units")
    )

    cycle = cycle.merge(baseline, on="product_name", how="left")
    cycle["seasonality_index"] = cycle["cycle_avg_units"] / cycle["avg_units"]

    pivot = cycle.pivot_table(
        index="product_name",
        columns="cycle_position",
        values="seasonality_index",
        aggfunc="mean"
    ).fillna(0)

    plt.figure(figsize=(10, 6))
    plt.imshow(pivot, aspect="auto")
    plt.colorbar(label="Seasonality Index")

    plt.xlabel("Week Position in 4-Week Cycle")
    plt.ylabel("Product")
    plt.title("Product Demand Seasonality Index")

    path = FIGURES_DIR / "product_demand_seasonality_index.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def plot_prophet_forecast() -> Path | None:
    series = build_normalized_department_series(exclude_week_zero=True)

    if series.empty or len(series) < 12:
        print("Not enough data for Prophet forecast.")
        return None

    df = series.reset_index()
    df.columns = ["relative_week_index", "y"]

    # pseudo-date hebdomadaire
    anchor_date = pd.Timestamp("2020-01-06")
    df["ds"] = anchor_date + pd.to_timedelta((df["relative_week_index"] - 1) * 7, unit="D")

    prophet_df = df[["ds", "y"]].copy()

    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False
    )

    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=12, freq="W-MON")
    forecast = model.predict(future)

    plt.figure(figsize=(10, 6))
    plt.plot(prophet_df["ds"], prophet_df["y"], label="Actual")
    plt.plot(forecast["ds"], forecast["yhat"], linestyle="--", label="Prophet forecast")

    plt.xlabel("Pseudo Weekly Date")
    plt.ylabel("Units per Order")
    plt.title("Prophet Demand Forecast")
    plt.legend()

    path = FIGURES_DIR / "prophet_forecast.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def generate_html_report(image_paths: list[Path]) -> Path:
    html_path = REPORT_DIR / "demand_forecasting_report.html"

    total_products = product_demand["product_id"].nunique()
    total_departments = department_demand["department"].nunique()

    product_totals = (
        product_demand.groupby("product_name")["units_sold"]
        .sum()
        .sort_values(ascending=False)
    )
    department_totals = (
        department_demand.groupby("department")["units_sold"]
        .sum()
        .sort_values(ascending=False)
    )

    top_product = product_totals.index[0] if not product_totals.empty else "N/A"
    top_product_units = int(product_totals.iloc[0]) if not product_totals.empty else 0

    top_department = department_totals.index[0] if not department_totals.empty else "N/A"
    top_department_units = int(department_totals.iloc[0]) if not department_totals.empty else 0

    avg_product_weekly_units = round(product_demand["units_sold"].mean(), 2) if not product_demand.empty else 0
    avg_department_weekly_units = round(department_demand["units_sold"].mean(), 2) if not department_demand.empty else 0

    observed_product_weeks = (
        int(product_demand["relative_week_index"].nunique())
        if not product_demand.empty else 0
    )

    observed_department_weeks = (
        int(department_demand["relative_week_index"].nunique())
        if not department_demand.empty else 0
    )

    total_product_units = (
        int(product_demand["units_sold"].sum())
        if not product_demand.empty else 0
    )

    total_department_units = (
        int(department_demand["units_sold"].sum())
        if not department_demand.empty else 0
    )

    top_product_share = (
        round((top_product_units / total_product_units) * 100, 1)
        if total_product_units > 0 else 0
    )

    top_department_share = (
        round((top_department_units / total_department_units) * 100, 1)
        if total_department_units > 0 else 0
    )

    descriptions = {
        "product_demand_trends": "Shows the historical weekly demand evolution for the selected top products using the relative time axis reconstructed from Instacart orders.",
        "department_demand_trends": "Compares weekly unit demand across departments to highlight broader category-level trends.",
        "top_products_total_demand": "Ranks the selected products by total units sold across the available weekly history.",
        "top_departments_total_demand": "Ranks departments by total units sold to highlight the strongest contributors to demand volume.",
        "moving_average_forecast": "Applies a 4-week moving average to product demand trends to provide a simple baseline forecast for future demand.",
        "weekly_demand_evolution": "Displays the distribution of weekly demand across all products and departments.",
        "demand_anomalies": "Identifies weeks where total demand significantly deviated from the average, which may indicate anomalies or special events.",
        "product_peak_weeks": "Shows the reconstructed relative week in which each selected product reaches its highest observed demand, excluding week 0 to reduce cohort alignment bias.",
        "department_peak_weeks": "Shows the reconstructed relative week in which each department reaches its highest observed demand, excluding week 0 to reduce cohort alignment bias.",
        "weekly_demand_pattern": "Displays the overall weekly demand pattern across all products and departments.",
        "replenishment_cycle_pattern": "Shows the 4-week replenishment cycle pattern across all products and departments.",
        "product_demand_heatmap": "Visualizes the demand for each product across different weeks using a heatmap.",
        "demand_acf": "Displays the autocorrelation function (ACF) of the demand series to identify temporal dependencies.",
        "product_series_banana": "Shows the weekly reconstructed demand series for Banana before forecasting.",
        "normalized_department_series": "Displays department demand normalized by order volume to reduce cohort decay effects.",
        "arima_forecast_banana": "Applies an ARIMA baseline forecast to the Banana demand series.",
        "arima_forecast_normalized_department": "Applies an ARIMA baseline forecast to normalized department demand.",
        "stl_decomposition": "STL decomposition separating trend, seasonal component, and residual noise in the normalized department demand series.",
        "reorder_interval_distribution": "Displays the distribution of reorder intervals across all customers.",
        "customer_reorder_segmentation": "Segments customers by their average reorder interval to identify weekly, bi-weekly, monthly, and long-interval shopping behaviors.",
        "customer_lifetime_ordering_curve": "Shows how the number of active customers declines across the reconstructed relative timeline.",
        "reorder_interval_distribution_capped": "Displays the distribution of days between orders and highlights the 30-day cap applied by the source dataset.",
        "reorder_survival_curve": "Shows the probability of a customer reordering as a function of time since their last order.",
        "customer_reorder_cohorts": "Shows customer reorder retention across cohort start weeks and weeks since first observed order.",
        "product_demand_seasonality_index": "Compares each product's relative demand intensity across positions in the reconstructed 4-week demand cycle.",
        "prophet_forecast": "Uses Prophet to project normalized department demand trend on a pseudo-weekly timeline derived from relative weeks.",
    }

    cards_html = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Products Analyzed</div>
            <div class="kpi-value">{total_products:,}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Departments Analyzed</div>
            <div class="kpi-value">{total_departments:,}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Weekly Product Demand</div>
            <div class="kpi-value">{avg_product_weekly_units}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Weekly Department Demand</div>
            <div class="kpi-value">{avg_department_weekly_units}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Top Product</div>
            <div class="kpi-value small">{top_product}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Top Department</div>
            <div class="kpi-value small">{top_department}</div>
        </div>
    </div>

    <h2 class="section-title">Key Insights</h2>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Highest Product Volume</div>
            <div class="kpi-value small">{top_product} ({top_product_units:,} units)</div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Highest Department Volume</div>
            <div class="kpi-value small">{top_department} ({top_department_units:,} units)</div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Total Exported Product Units</div>
            <div class="kpi-value small">{total_product_units:,}</div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Total Exported Department Units</div>
            <div class="kpi-value small">{total_department_units:,}</div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Observed Relative Weeks</div>
            <div class="kpi-value small">
                Products: {observed_product_weeks} · Departments: {observed_department_weeks}
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Top Product Share of Volume</div>
            <div class="kpi-value small">{top_product_share}% of exported product demand</div>
        </div>
    </div>
    """

    ordered_chart_keys = [
        "product_demand_trends",
        "department_demand_trends",
        "top_products_total_demand",
        "top_departments_total_demand",
        "moving_average_forecast",
        "weekly_demand_evolution",
        "demand_anomalies",
        "product_peak_weeks",
        "department_peak_weeks",
        "weekly_demand_pattern",
        "replenishment_cycle_pattern",
        "product_demand_heatmap",
        "demand_acf",
        "stl_decomposition",
        "reorder_interval_distribution",
        "reorder_interval_distribution_capped",
        "customer_reorder_segmentation",
        "customer_lifetime_ordering_curve",
        "customer_reorder_cohorts",
        "product_demand_seasonality_index",
        "prophet_forecast",
    ]

    image_map = {path.stem: path for path in image_paths}

    image_blocks = []
    for chart_key in ordered_chart_keys:
        path = image_map.get(chart_key)
        if not path:
            continue

        title = chart_key.replace("_", " ").title()
        relative_path = f"figures/{path.name}"
        description = descriptions.get(chart_key, "Demand forecasting visualization.")

        image_blocks.append(f"""
        <article class="chart-card">
            <h2>{title}</h2>
            <p class="chart-description">{description}</p>
            <img src="{relative_path}" alt="{title}" class="zoomable">
        </article>
        """)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demand Forecasting Report</title>
    <style>
        :root {{
            --bg: #f6f8fb;
            --card: #ffffff;
            --text: #1f2937;
            --muted: #6b7280;
            --border: #e5e7eb;
            --shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
            --radius: 16px;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 32px 20px 48px;
        }}

        .hero {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 28px;
            margin-bottom: 24px;
        }}

        .hero h1 {{
            margin: 0 0 12px;
            font-size: 2rem;
        }}

        .hero p {{
            margin: 0;
            color: var(--muted);
            max-width: 820px;
        }}

        .meta {{
            margin-top: 16px;
            font-size: 0.95rem;
            color: var(--muted);
        }}

        .section-title {{
            margin: 28px 0 16px;
            font-size: 1.35rem;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }}

        .kpi-card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 18px;
        }}

        .kpi-label {{
            font-size: 0.9rem;
            color: var(--muted);
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-size: 1.35rem;
            font-weight: bold;
            word-break: break-word;
        }}

        .kpi-value.small {{
            font-size: 1rem;
            line-height: 1.4;
        }}

        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 20px;
        }}

        .chart-card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 20px;
        }}

        .chart-card h2 {{
            margin-top: 0;
            margin-bottom: 8px;
            font-size: 1.2rem;
        }}

        .chart-description {{
            margin-top: 0;
            margin-bottom: 16px;
            color: var(--muted);
            font-size: 0.95rem;
        }}

        .chart-card img {{
            width: 100%;
            height: auto;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: #fff;
            cursor: zoom-in;
            transition: transform 0.2s ease;
            max-height: 420px;
            object-fit: contain;
        }}

        .chart-card img:hover {{
            transform: scale(1.01);
        }}

        .image-modal {{
            display: none;
            position: fixed;
            z-index: 999;
            padding-top: 40px;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }}

        .image-modal img {{
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 85%;
        }}

        .image-modal span {{
            position: absolute;
            top: 25px;
            right: 40px;
            color: white;
            font-size: 32px;
            cursor: pointer;
        }}

        .footer {{
            margin-top: 32px;
            color: var(--muted);
            font-size: 0.9rem;
            text-align: center;
        }}

        .interpretation-card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 24px;
            margin-top: 28px;
        }}

        @media (max-width: 640px) {{
            .hero h1 {{
                font-size: 1.6rem;
            }}

            .chart-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <section class="hero">
            <h1>Demand Forecasting Report</h1>
            <p>
                This report presents weekly product and department demand trends derived from the Instacart dataset.
                Because the source data does not include true calendar dates, demand was reconstructed on a relative
                weekly timeline using customer order sequences and days-since-prior-order logic in DuckDB. These
                trend views provide a foundation for future forecasting models and demand planning analysis.
            </p>
            <div class="meta">Generated on {generated_at}</div>
        </section>

        <h2 class="section-title">Key Metrics</h2>
        {cards_html}

        <h2 class="section-title">Visual Insights</h2>
        <section class="chart-grid">
            {''.join(image_blocks)}
        </section>

        <section class="interpretation-card">
        <h2 class="section-title">How to Interpret These Results</h2>

            <p>
            <strong>Relative Week Index</strong> represents a reconstructed weekly position in each customer's order journey,
            not a true shared calendar week. This means week-level comparisons reflect aligned customer progression rather
            than real-world seasonality.
            </p>

            <p>
            <strong>Units Sold</strong> measures the total number of product rows observed in weekly order activity.
            </p>

            <p>
            <strong>Orders Count</strong> counts distinct orders containing a product or department during a given relative week.
            </p>

            <p>
            <strong>Peak Relative Week</strong> indicates the reconstructed week in which a product or department reaches
            its highest observed demand within the relative customer timeline. It does not represent a true calendar
            week of the year.
            </p>

            <p>
            <strong>Week 0 Exclusion</strong> removes the cohort-aligned starting week shared by nearly all customers,
            which otherwise dominates the relative timeline and can hide more meaningful later demand peaks.
            </p>

            <p>
            The reorder interval analysis reveals several distinct shopping rhythms, including weekly, bi-weekly, and monthly behaviors. 
            The strong spike at 30 days should be interpreted carefully, as the source dataset caps reorder intervals at 30 days. 
            The customer lifetime ordering curve also explains why aggregate relative-week demand declines over time: fewer customers remain observable in later weeks of the reconstructed timeline.
            </p>

            <p>
            <strong>Customer Reorder Cohorts</strong> show how reorder activity declines across customer groups after their first observed order, highlighting retention patterns in the reconstructed timeline.
            </p>

            <p>
            <strong>Product Demand Seasonality Index</strong> compares each product's demand intensity across positions in the relative 4-week cycle. It reflects cyclical behavior in reconstructed time, not true calendar seasonality.
            </p>

            <p>
            <strong>Prophet Forecast</strong> is applied on a pseudo-weekly timeline to project trend behavior. Because the source dataset does not contain real calendar dates, the forecast should be interpreted as a relative demand projection rather than a real-world seasonal calendar forecast.
            </p>
        </section>

        <h2 class="section-title">Key Analytical Takeaways</h2>

        <ul>
        <li>Customer ordering behavior clusters around weekly, bi-weekly, and monthly shopping cycles.</li>
        <li>The Instacart dataset caps reorder intervals at 30 days, which creates an artificial spike in the distribution.</li>
        <li>Demand patterns show limited seasonality but a mild upward trend in normalized units per order.</li>
        <li>Customer retention gradually declines across relative weeks, explaining decreasing aggregate demand later in the timeline.</li>
        <li>Forecasting models therefore focus primarily on trend projection rather than calendar seasonality.</li>
        </ul>

        <h2 class="section-title">Methodology</h2>

        <p>
        This analysis reconstructs a relative weekly timeline using customer order sequences and the
        days_since_prior_order field. Because the Instacart dataset does not contain real calendar
        dates, all time-series analyses are performed on relative customer timelines.
        </p>

        <p>
        Demand analytics, cohort analysis, and forecasting models are built on a DuckDB analytical
        warehouse using a star schema centered on order-product relationships.
        </p>

        <div class="footer">
            Retail Analytic Platform · Demand Forecasting
        </div>
    </div>

    <div id="imgModal" class="image-modal">
        <span id="closeModal">&times;</span>
        <img id="modalImage">
    </div>

    <script>
        const modal = document.getElementById("imgModal");
        const modalImg = document.getElementById("modalImage");
        const closeBtn = document.getElementById("closeModal");

        document.querySelectorAll(".zoomable").forEach(img => {{
            img.onclick = function() {{
                modal.style.display = "block";
                modalImg.src = this.src;
            }};
        }});

        closeBtn.onclick = function() {{
            modal.style.display = "none";
        }};

        modal.onclick = function(e) {{
            if (e.target === modal) {{
                modal.style.display = "none";
            }}
        }};
    </script>
</body>
</html>
"""

    html_path.write_text(html_content, encoding="utf-8")
    return html_path

def main():

    generated_files = []

    generated_files.append(plot_product_demand_trends())
    generated_files.append(plot_department_demand_trends())
    generated_files.append(plot_top_products())
    generated_files.append(plot_top_departments())
    generated_files.append(plot_product_forecast())
    generated_files.append(plot_weekly_demand_distribution())
    generated_files.append(plot_demand_anomalies())

    product_peak_chart = plot_product_peak_weeks()
    if product_peak_chart is not None:
        generated_files.append(product_peak_chart)

    department_peak_chart = plot_department_peak_weeks()
    if department_peak_chart is not None:
        generated_files.append(department_peak_chart)

    generated_files.append(plot_weekly_demand_pattern())
    generated_files.append(plot_replenishment_cycle())
    generated_files.append(plot_product_week_heatmap())
    generated_files.append(plot_demand_acf())

    product_series_chart = plot_product_series("Banana")
    if product_series_chart is not None:
        generated_files.append(product_series_chart)

    normalized_series_chart = plot_normalized_department_series()
    if normalized_series_chart is not None:
        generated_files.append(normalized_series_chart)

    arima_product_chart = plot_arima_product_forecast("Banana")
    if arima_product_chart is not None:
        generated_files.append(arima_product_chart)

    arima_normalized_chart = plot_arima_normalized_department_forecast()
    if arima_normalized_chart is not None:
        generated_files.append(arima_normalized_chart)
        
        stl_chart = plot_stl_decomposition(period=4)

    if stl_chart is not None:
        generated_files.append(stl_chart)

    generated_files.append(plot_reorder_interval_distribution())
    segmentation_chart = plot_customer_reorder_segmentation(customer_reorder)

    if segmentation_chart is not None:
        generated_files.append(segmentation_chart)

    generated_files.append(plot_customer_lifetime_ordering_curve(customer_lifetime_curve))
    generated_files.append(plot_reorder_interval_distribution_capped(reorder_intervals))
    generated_files.append(plot_reorder_interval_cdf(reorder_intervals))

    survival_chart = plot_reorder_survival_curve(reorder_intervals)

    if survival_chart is not None:
        generated_files.append(survival_chart)

    cohort_chart = plot_customer_reorder_cohorts(customer_reorder_cohorts)
    if cohort_chart is not None:
        generated_files.append(cohort_chart)

    seasonality_chart = plot_product_demand_seasonality_index(period=4)
    if seasonality_chart is not None:
        generated_files.append(seasonality_chart)

    prophet_chart = plot_prophet_forecast()
    if prophet_chart is not None:
        generated_files.append(prophet_chart)

    html_report = generate_html_report(generated_files)

    print("Visualizations generated:")

    for file_path in generated_files:
        print(file_path)

    print("\nHTML report generated:")
    print(html_report)


if __name__ == "__main__":
    main()