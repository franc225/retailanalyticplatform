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

        <div class="container">
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
                These demand trends provide a stable baseline for future forecasting methods such as moving averages,
                ARIMA, or Prophet.
                </p>
            </section>
        </div>

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

    html_report = generate_html_report(generated_files)

    print("Visualizations generated:")

    for file_path in generated_files:
        print(file_path)

    print("\nHTML report generated:")
    print(html_report)


if __name__ == "__main__":
    main()