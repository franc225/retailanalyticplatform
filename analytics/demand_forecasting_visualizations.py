from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]

EXPORT_DIR = BASE_DIR / "data" / "exports"
REPORT_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORT_DIR / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

product_demand = pd.read_parquet(EXPORT_DIR / "top_product_demand_timeseries.parquet")
department_demand = pd.read_parquet(EXPORT_DIR / "department_demand_timeseries.parquet")

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
        "product_demand_heatmap": "Visualizes the demand for each product across different weeks using a heatmap."

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
            These demand trends provide a stable baseline for future forecasting methods such as moving averages,
            ARIMA, or Prophet.
            </p>
        </section>

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

    html_report = generate_html_report(generated_files)

    print("Visualizations generated:")

    for file_path in generated_files:
        print(file_path)

    print("\nHTML report generated:")
    print(html_report)


if __name__ == "__main__":
    main()