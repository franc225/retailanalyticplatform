from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


# Paths
BASE_DIR = Path(__file__).resolve().parents[1]
EXPORT_DIR = BASE_DIR / "data" / "exports"
REPORT_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORT_DIR / "figures"

# Create output folders if they do not exist
REPORT_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def save_plot(filename: str) -> Path:
    """
    Save the current matplotlib figure to the reports/figures directory.
    """
    output_path = FIGURES_DIR / filename
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return output_path

def plot_orders_by_day() -> Path:
    df = pd.read_csv(EXPORT_DIR / "orders_by_day.csv")

    plt.figure(figsize=(8, 5))
    plt.bar(df["day_name"], df["total_orders"])
    plt.title("Orders by Day of Week")
    plt.xlabel("Day of Week")
    plt.ylabel("Total Orders")
    
    return save_plot("orders_by_day.png")

def plot_orders_by_hour() -> Path:
    df = pd.read_csv(EXPORT_DIR / "orders_by_hour.csv")

    plt.figure(figsize=(10, 5))
    plt.plot(df["order_hour_of_day"], df["total_orders"], marker="o")
    plt.title("Orders by Hour of Day")
    plt.xlabel("Hour of Day")
    plt.ylabel("Total Orders")

    return save_plot("orders_by_hour.png")

def plot_basket_size_distribution() -> Path:
    df = pd.read_csv(EXPORT_DIR / "basket_size_distribution.csv")

    # Optional: limit to smaller basket sizes for readability
    df = df[df["basket_size"] <= 40]

    plt.figure(figsize=(10, 5))
    plt.bar(df["basket_size"], df["total_orders"])
    plt.title("Basket Size Distribution")
    plt.xlabel("Basket Size")
    plt.ylabel("Number of Orders")

    return save_plot("basket_size_distribution.png")

def plot_top_products() -> Path:
    df = pd.read_csv(EXPORT_DIR / "product_summary.csv")

    top_df = df.sort_values("times_ordered", ascending=False).head(15)
    top_df = top_df.sort_values("times_ordered", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(top_df["product_name"], top_df["times_ordered"])
    plt.title("Top 15 Most Ordered Products")
    plt.xlabel("Times Ordered")
    plt.ylabel("Product")

    return save_plot("top_products.png")

def plot_top_departments() -> Path:
    df = pd.read_csv(EXPORT_DIR / "department_summary.csv")

    top_df = df.sort_values("total_items_ordered", ascending=False).head(10)
    top_df = top_df.sort_values("total_items_ordered", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(top_df["department"], top_df["total_items_ordered"])
    plt.title("Top 10 Departments by Items Ordered")
    plt.xlabel("Total Items Ordered")
    plt.ylabel("Department")

    return save_plot("top_departments.png")

def plot_customer_order_distribution() -> Path:
    df = pd.read_csv(EXPORT_DIR / "customer_summary.csv")

    bins = [0, 1, 5, 10, 20, 50, 100]
    labels = ["1", "2-5", "6-10", "11-20", "21-50", "51-100"]
    df["order_band"] = pd.cut(df["total_orders"], bins=bins, labels=labels)

    summary = df["order_band"].value_counts().sort_index()

    plt.figure(figsize=(8, 5))
    plt.bar(summary.index.astype(str), summary.values)
    plt.title("Customer Distribution by Number of Orders")
    plt.xlabel("Order Count Band")
    plt.ylabel("Number of Customers")

    return save_plot("customer_order_distribution.png")

def generate_html_report(image_paths: list[Path]) -> Path:
    html_path = REPORT_DIR / "retail_analytics_report.html"

    customer_df = pd.read_csv(EXPORT_DIR / "customer_summary.csv")
    day_df = pd.read_csv(EXPORT_DIR / "orders_by_day.csv")
    hour_df = pd.read_csv(EXPORT_DIR / "orders_by_hour.csv")
    department_df = pd.read_csv(EXPORT_DIR / "department_summary.csv")
    product_df = pd.read_csv(EXPORT_DIR / "product_summary.csv")

    total_customers = len(customer_df)
    avg_basket_size = round(customer_df["avg_basket_size"].mean(), 2)
    top_day = day_df.sort_values("total_orders", ascending=False).iloc[0]["day_name"]
    peak_hour = int(hour_df.sort_values("total_orders", ascending=False).iloc[0]["order_hour_of_day"])
    total_departments = department_df["department"].nunique()
    top_product = product_df.sort_values("times_ordered", ascending=False).iloc[0]["product_name"]

    descriptions = {
        "orders_by_day": "Shows weekly ordering patterns and highlights the most active shopping days.",
        "orders_by_hour": "Highlights peak ordering hours and daily customer shopping behavior.",
        "basket_size_distribution": "Shows how large customer baskets typically are and how concentrated demand is.",
        "top_products": "Ranks the most frequently ordered products across all customer orders.",
        "top_departments": "Summarizes the departments generating the highest item volume.",
        "customer_order_distribution": "Provides a simple segmentation of customers based on ordering frequency."
    }

    cards_html = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Customers</div>
            <div class="kpi-value">{total_customers:,}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Basket Size</div>
            <div class="kpi-value">{avg_basket_size}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Top Shopping Day</div>
            <div class="kpi-value">{top_day}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Peak Hour</div>
            <div class="kpi-value">{peak_hour}:00</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Departments</div>
            <div class="kpi-value">{total_departments}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Top Product</div>
            <div class="kpi-value">{top_product}</div>
        </div>
    </div>
    """

    image_blocks = []
    for path in image_paths:
        chart_key = path.stem
        title = chart_key.replace("_", " ").title()
        relative_path = f"figures/{path.name}"
        description = descriptions.get(chart_key, "Analytical visualization generated from aggregated retail data.")

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
    <title>Retail Analytics Report</title>
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
            max-width: 800px;
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
            font-size: 1.4rem;
            font-weight: bold;
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
        }}

        .footer {{
            margin-top: 32px;
            color: var(--muted);
            font-size: 0.9rem;
            text-align: center;
        }}

        @media (max-width: 640px) {{
            .hero h1 {{
                font-size: 1.6rem;
            }}

            .chart-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .zoomable {{
            cursor: zoom-in;
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
    </style>
</head>
<body>
    <div class="container">
        <section class="hero">
            <h1>Retail Analytics Report</h1>
            <p>
                This report presents exploratory retail analytics built from the Instacart Market Basket dataset.
                The analysis is based on a DuckDB star schema and aggregated reporting views exported to CSV,
                then visualized with Python and Matplotlib.
            </p>
            <div class="meta">Generated on {generated_at}</div>
        </section>

        <h2 class="section-title">Key Metrics</h2>
        {cards_html}

        <h2 class="section-title">Visual Insights</h2>
        <section class="chart-grid">
            {''.join(image_blocks)}
        </section>

        <div class="footer">
            Retail Analytic Platform · Instacart Market Basket
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

def main() -> None:
    generated_files = []

    generated_files.append(plot_orders_by_day())
    generated_files.append(plot_orders_by_hour())
    generated_files.append(plot_basket_size_distribution())
    generated_files.append(plot_top_products())
    generated_files.append(plot_top_departments())
    generated_files.append(plot_customer_order_distribution())

    html_report = generate_html_report(generated_files)

    print("Visualizations generated:")
    for file_path in generated_files:
        print(f"- {file_path}")

    print(f"\nHTML report generated:\n- {html_report}")


if __name__ == "__main__":
    main()