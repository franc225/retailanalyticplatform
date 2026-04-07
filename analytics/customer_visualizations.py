from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]

EXPORT_DIR = BASE_DIR / "data" / "exports"
REPORT_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORT_DIR / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

customer_frequency = pd.read_csv(EXPORT_DIR / "customer_frequency.csv")
customer_reorder = pd.read_csv(EXPORT_DIR / "customer_reorder.csv")
customer_segments = pd.read_csv(EXPORT_DIR / "customer_segments.csv")

customer_metrics_path = EXPORT_DIR / "customer_metrics.csv"
customer_metrics = pd.read_csv(customer_metrics_path) if customer_metrics_path.exists() else None


def save_plot(filename: str) -> Path:
    path = FIGURES_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def plot_orders_per_customer_distribution() -> Path:
    df = customer_frequency.copy()

    # Optional readability filter
    df = df[df["total_orders"] <= 50]

    plt.figure(figsize=(9, 5))
    plt.hist(df["total_orders"], bins=30)

    plt.xlabel("Total Orders per Customer")
    plt.ylabel("Number of Customers")
    plt.title("Purchase Frequency Distribution")

    return save_plot("orders_per_customer_distribution.png")


def plot_reorder_rate_distribution() -> Path:
    df = customer_reorder.copy()

    plt.figure(figsize=(9, 5))
    plt.hist(df["reorder_rate"], bins=30)

    plt.xlabel("Reorder Rate")
    plt.ylabel("Number of Customers")
    plt.title("Reorder Rate Distribution")

    return save_plot("reorder_rate_distribution.png")


def plot_orders_vs_reorder_rate() -> Path:
    df = customer_reorder.copy()

    # Optional readability filter
    df = df[df["total_orders"] <= 100]

    plt.figure(figsize=(8, 6))
    plt.scatter(
        df["total_orders"],
        df["reorder_rate"],
        alpha=0.4
    )

    plt.xlabel("Total Orders")
    plt.ylabel("Reorder Rate")
    plt.title("Orders vs Reorder Rate")

    return save_plot("orders_vs_reorder_rate.png")


def plot_customer_segments() -> Path:
    df = customer_segments.copy()

    summary = (
        df["customer_segment"]
        .value_counts()
        .reindex(
            [
                "Occasional Customers",
                "Regular Customers",
                "Frequent Customers",
                "Power Users",
            ],
            fill_value=0
        )
    )

    plt.figure(figsize=(8, 5))
    plt.bar(summary.index.astype(str), summary.values)

    plt.xlabel("Customer Segment")
    plt.ylabel("Number of Customers")
    plt.title("Customer Segmentation")

    plt.xticks(rotation=15)

    return save_plot("customer_segments.png")


def plot_avg_basket_size_by_segment() -> Path:
    if customer_metrics is None:
        raise ValueError("customer_metrics.csv is required for this visualization.")

    df = customer_metrics.merge(customer_segments, on="customer_id", how="inner")

    summary = (
        df.groupby("customer_segment", as_index=False)["avg_basket_size"]
        .mean()
    )

    segment_order = [
        "Occasional Customers",
        "Regular Customers",
        "Frequent Customers",
        "Power Users",
    ]
    summary["customer_segment"] = pd.Categorical(
        summary["customer_segment"],
        categories=segment_order,
        ordered=True,
    )
    summary = summary.sort_values("customer_segment")

    plt.figure(figsize=(8, 5))
    plt.bar(summary["customer_segment"], summary["avg_basket_size"])

    plt.xlabel("Customer Segment")
    plt.ylabel("Average Basket Size")
    plt.title("Average Basket Size by Customer Segment")

    plt.xticks(rotation=15)

    return save_plot("avg_basket_size_by_segment.png")


def plot_avg_days_between_orders_by_segment() -> Path:
    if customer_metrics is None:
        raise ValueError("customer_metrics.csv is required for this visualization.")

    df = customer_metrics.merge(customer_segments, on="customer_id", how="inner")

    summary = (
        df.groupby("customer_segment", as_index=False)["avg_days_between_orders"]
        .mean()
    )

    segment_order = [
        "Occasional Customers",
        "Regular Customers",
        "Frequent Customers",
        "Power Users",
    ]
    summary["customer_segment"] = pd.Categorical(
        summary["customer_segment"],
        categories=segment_order,
        ordered=True,
    )
    summary = summary.sort_values("customer_segment")

    plt.figure(figsize=(8, 5))
    plt.bar(summary["customer_segment"], summary["avg_days_between_orders"])

    plt.xlabel("Customer Segment")
    plt.ylabel("Average Days Between Orders")
    plt.title("Average Days Between Orders by Customer Segment")

    plt.xticks(rotation=15)

    return save_plot("avg_days_between_orders_by_segment.png")

def plot_basket_size_distribution():

    if customer_metrics is None:
        return None

    plt.figure(figsize=(9,5))
    plt.hist(customer_metrics["avg_basket_size"], bins=30)

    plt.xlabel("Average Basket Size")
    plt.ylabel("Number of Customers")
    plt.title("Basket Size Distribution")

    path = FIGURES_DIR / "basket_size_distribution.png"

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path


def generate_html_report(image_paths: list[Path]) -> Path:
    html_path = REPORT_DIR / "customer_analytics_report.html"

    total_customers = len(customer_segments)
    avg_orders = round(customer_reorder["total_orders"].mean(), 2)
    avg_reorder_rate = round(customer_reorder["reorder_rate"].mean(), 3)
    largest_segment = customer_segments["customer_segment"].value_counts().idxmax()

    avg_basket_size = (
        round(customer_metrics["avg_basket_size"].mean(), 2)
        if customer_metrics is not None else "N/A"
    )

    avg_days_between_orders = (
        round(customer_metrics["avg_days_between_orders"].mean(), 2)
        if customer_metrics is not None else "N/A"
    )

    # Segment engagement insights
    if customer_metrics is not None:
        df = (
            customer_segments
            .merge(customer_metrics, on="customer_id", how="inner")
            .merge(customer_reorder, on="customer_id", how="inner", suffixes=("_metrics", "_reorder"))
        )

        # Normalise column names after merge
        if "total_orders" not in df.columns:
            if "total_orders_reorder" in df.columns:
                df["total_orders"] = df["total_orders_reorder"]
            elif "total_orders_metrics" in df.columns:
                df["total_orders"] = df["total_orders_metrics"]

        if "reorder_rate" not in df.columns:
            if "reorder_rate_reorder" in df.columns:
                df["reorder_rate"] = df["reorder_rate_reorder"]
            elif "reorder_rate_metrics" in df.columns:
                df["reorder_rate"] = df["reorder_rate_metrics"]
            elif "reorder_rate_x" in df.columns:
                df["reorder_rate"] = df["reorder_rate_x"]
            elif "reorder_rate_y" in df.columns:
                df["reorder_rate"] = df["reorder_rate_y"]

        required_cols = [
            "customer_segment",
            "total_orders",
            "reorder_rate",
            "avg_basket_size",
            "avg_days_between_orders",
        ]

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Missing required columns after merge: {missing_cols}. Available columns: {list(df.columns)}")
        
        segment_stats = (
            df.groupby("customer_segment")
            .agg(
                customers=("customer_id", "count"),
                avg_orders=("total_orders", "mean"),
                avg_reorder_rate=("reorder_rate", "mean"),
                avg_basket_size=("avg_basket_size", "mean"),
                avg_days_between_orders=("avg_days_between_orders", "mean"),
            )
        )

        top_segment = segment_stats["avg_orders"].idxmax()
        top_segment_orders = round(segment_stats["avg_orders"].max(), 2)

        top_basket_segment = segment_stats["avg_basket_size"].idxmax()
        top_basket_value = round(segment_stats["avg_basket_size"].max(), 2)

        top_reorder_segment = segment_stats["avg_reorder_rate"].idxmax()
        top_reorder_value = round(segment_stats["avg_reorder_rate"].max(), 3)

        engagement_insight = (
            f"The most engaged customer segment is <strong>{top_segment}</strong>, "
            f"with an average of <strong>{top_segment_orders}</strong> orders per customer."
        )

        basket_insight = (
            f"The segment with the largest baskets is <strong>{top_basket_segment}</strong>, "
            f"with an average basket size of <strong>{top_basket_value}</strong>."
        )

        reorder_insight = (
            f"The segment with the strongest reorder behavior is <strong>{top_reorder_segment}</strong>, "
            f"with an average reorder rate of <strong>{top_reorder_value}</strong>."
        )
    else:
        top_segment = "N/A"
        top_segment_orders = "N/A"
        top_basket_segment = "N/A"
        top_basket_value = "N/A"
        top_reorder_segment = "N/A"
        top_reorder_value = "N/A"

        engagement_insight = (
            "Customer engagement insight is unavailable because customer_metrics.csv was not provided."
        )

        basket_insight = (
            "Basket-size segment insight is unavailable because customer_metrics.csv was not provided."
        )

        reorder_insight = (
            "Reorder behavior insight is unavailable because customer_metrics.csv was not provided."
        )

    cards_html = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Customers</div>
            <div class="kpi-value">{total_customers:,}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Orders per Customer</div>
            <div class="kpi-value">{avg_orders}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Reorder Rate</div>
            <div class="kpi-value">{avg_reorder_rate}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Largest Segment</div>
            <div class="kpi-value small">{largest_segment}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Basket Size</div>
            <div class="kpi-value">{avg_basket_size}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Days Between Orders</div>
            <div class="kpi-value">{avg_days_between_orders}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Highest Engagement Segment</div>
            <div class="kpi-value small">{top_segment}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Highest Basket Size Segment</div>
            <div class="kpi-value small">{top_basket_segment}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Highest Reorder Segment</div>
            <div class="kpi-value small">{top_reorder_segment}</div>
        </div>
    </div>

    <h2 class="section-title">Key Insights</h2>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Customer Behavior Focus</div>
            <div class="kpi-value small">
                Purchase frequency, reorder behavior, and simple behavioral segmentation
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Largest Customer Group</div>
            <div class="kpi-value small">
                {largest_segment}
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Average Customer Activity</div>
            <div class="kpi-value small">
                {avg_orders} orders per customer
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Typical Reorder Behavior</div>
            <div class="kpi-value small">
                Average reorder rate of {avg_reorder_rate}
            </div>
        </div>
    </div>

        <h2 class="section-title">Business Insights</h2>

    <div class="kpi-card">
        <p>
        <strong>Engagement:</strong> Power Users represent the most active customers,
        averaging 68.93 orders per customer. These customers likely drive a
        disproportionate share of demand and are prime candidates for loyalty programs.
        </p>

        <p>
        <strong>Basket behavior:</strong> Frequent Customers show the largest baskets,
        suggesting consistent purchasing routines and strong cross-category demand.
        </p>

        <p>
        <strong>Reorder patterns:</strong> Power Users demonstrate the strongest
        reorder behavior, indicating habitual purchasing and potential brand loyalty.
        </p>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Engagement Insight</div>
            <div class="kpi-value small">
                {engagement_insight}
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Basket Insight</div>
            <div class="kpi-value small">
                {basket_insight}
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Reorder Insight</div>
            <div class="kpi-value small">
                {reorder_insight}
            </div>
        </div>
    </div>
    """

    descriptions = {
        "orders_per_customer_distribution": "Shows how frequently customers place orders across the dataset.",
        "reorder_rate_distribution": "Shows how strongly customers tend to repurchase previously ordered products.",
        "orders_vs_reorder_rate": "Compares purchase frequency and reorder behavior across customers.",
        "customer_segments": "Shows the distribution of customers across predefined behavioral segments.",
        "avg_basket_size_by_segment": "Compares average basket size across customer segments.",
        "avg_days_between_orders_by_segment": "Compares ordering cadence across customer segments.",
        "basket_size_distribution": "Shows how average basket size varies across customers.",
    }

    ordered_chart_keys = [
        "orders_per_customer_distribution",
        "reorder_rate_distribution",
        "orders_vs_reorder_rate",
        "customer_segments",
        "avg_basket_size_by_segment",
        "avg_days_between_orders_by_segment",
        "basket_size_distribution",
    ]

    image_map = {path.stem: path for path in image_paths}

    titles = {
        "orders_per_customer_distribution": "Purchase Frequency Distribution",
        "reorder_rate_distribution": "Customer Reorder Behavior",
        "orders_vs_reorder_rate": "Orders vs Reorder Rate",
        "customer_segments": "Customer Segmentation",
        "avg_basket_size_by_segment": "Basket Size by Segment",
        "avg_days_between_orders_by_segment": "Ordering Frequency by Segment",
        "basket_size_distribution": "Basket Size Distribution",
    }

    image_blocks = []
    for chart_key in ordered_chart_keys:
        path = image_map.get(chart_key)
        if not path:
            continue

        title = titles.get(chart_key, chart_key.replace("_", " ").title())
        relative_path = f"figures/{path.name}"
        description = descriptions.get(chart_key, "Customer analytics visualization.")

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
    <title>Customer Analytics Report</title>
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
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
            line-height: 1.5;
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
            <h1>Customer Analytics Report</h1>
            <p>
                This report analyzes customer behavior from the Instacart Market Basket dataset.
                It focuses on purchase frequency, reorder behavior, and customer segmentation
                using aggregated customer metrics exported from DuckDB and visualized with Python and Matplotlib.
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
            Retail Analytic Platform · Customer Analytics
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

    <h2 class="section-title">How to Interpret These Results</h2>

    <p>
    <strong>Purchase frequency</strong> shows how often customers place orders.
    Customers with more orders tend to contribute more stable long-term demand.
    </p>

    <p>
    <strong>Reorder rate</strong> measures how strongly customers repurchase previously ordered products.
    Higher values suggest more routine or habitual purchasing behavior.
    </p>

    <p>
    <strong>Customer segments</strong> group customers based on ordering frequency.
    This helps identify occasional buyers, regulars, and high-value repeat customers.
    </p>
</body>
</html>
"""
    html_path.write_text(html_content, encoding="utf-8")
    return html_path


def main() -> None:
    generated_files = []

    generated_files.append(plot_orders_per_customer_distribution())
    generated_files.append(plot_reorder_rate_distribution())
    generated_files.append(plot_orders_vs_reorder_rate())
    generated_files.append(plot_customer_segments())

    if customer_metrics is not None:
        generated_files.append(plot_avg_basket_size_by_segment())
        generated_files.append(plot_avg_days_between_orders_by_segment())

    generated_files.append(plot_basket_size_distribution())

    html_report = generate_html_report(generated_files)

    print("Visualizations generated:")
    for file_path in generated_files:
        print(f"- {file_path}")

    print(f"\nHTML report generated:\n- {html_report}")


if __name__ == "__main__":
    main()