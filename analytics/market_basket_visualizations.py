from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

BASE_DIR = Path(__file__).resolve().parents[1]

EXPORT_DIR = BASE_DIR / "data" / "exports"
REPORT_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORT_DIR / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

rules = pd.read_csv(EXPORT_DIR / "association_rules.csv")

rules = rules.sort_values("lift", ascending=False)

def plot_top_association_rules():

    df = rules.sort_values("lift", ascending=False).head(20)

    labels = df["product_1_name"] + " → " + df["product_2_name"]

    plt.figure(figsize=(10,6))
    plt.barh(labels[::-1], df["lift"][::-1])

    plt.xlabel("Lift")
    plt.title("Top Product Association Rules")

    path = FIGURES_DIR / "top_association_rules.png"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def plot_lift_distribution():

    plt.figure(figsize=(8,5))
    plt.hist(rules["lift"], bins=30)

    plt.xlabel("Lift")
    plt.ylabel("Frequency")
    plt.title("Lift Distribution of Association Rules")

    path = FIGURES_DIR / "lift_distribution.png"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def plot_support_confidence():

    plt.figure(figsize=(8,6))

    plt.scatter(
        rules["support"],
        rules["confidence"],
        alpha=0.5
    )

    plt.xlabel("Support")
    plt.ylabel("Confidence")
    plt.title("Support vs Confidence")

    path = FIGURES_DIR / "support_vs_confidence.png"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def plot_cross_sell():

    df = rules[
        (rules["lift"] > 1.5) &
        (rules["confidence"] > 0.1)
    ].head(15)

    labels = df["product_1_name"] + " → " + df["product_2_name"]

    plt.figure(figsize=(10,6))
    plt.barh(labels[::-1], df["confidence"][::-1])

    plt.xlabel("Confidence")
    plt.title("Cross-Sell Opportunities")

    path = FIGURES_DIR / "cross_sell_opportunities.png"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def plot_product_network():

    df = rules[
        (rules["lift"] > 2) &
        (rules["confidence"] > 0.1)
    ].copy()

    df = df.sort_values("lift", ascending=False).head(40)

    G = nx.Graph()

    for _, row in df.iterrows():

        p1 = row["product_1_name"]
        p2 = row["product_2_name"]
        weight = row["lift"]

        G.add_edge(p1, p2, weight=weight)

    plt.figure(figsize=(12,10))

    pos = nx.spring_layout(G, k=0.5, seed=42)

    weights = [G[u][v]["weight"] for u,v in G.edges()]

    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=600,
        node_color="lightblue"
    )

    nx.draw_networkx_edges(
        G,
        pos,
        width=[w*0.3 for w in weights],
        alpha=0.7
    )

    nx.draw_networkx_labels(
        G,
        pos,
        font_size=8
    )

    plt.title("Product Association Network")

    path = FIGURES_DIR / "product_network.png"

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

    return path

def plot_rule_quality_quadrant() -> Path:
    df = rules.copy()

    plt.figure(figsize=(9, 6))
    plt.scatter(
        df["confidence"],
        df["lift"],
        s=df["pair_count"] * 2,
        alpha=0.5
    )

    plt.xlabel("Confidence")
    plt.ylabel("Lift")
    plt.title("Rule Quality Quadrant")

    path = FIGURES_DIR / "rule_quality_quadrant.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def plot_top_rules_by_confidence() -> Path:
    df = rules.sort_values(["confidence", "lift"], ascending=False).head(15).copy()

    p1_col = "product_1_name" if "product_1_name" in df.columns else "product_1"
    p2_col = "product_2_name" if "product_2_name" in df.columns else "product_2"

    labels = df[p1_col].astype(str) + " → " + df[p2_col].astype(str)

    plt.figure(figsize=(10, 6))
    plt.barh(labels[::-1], df["confidence"][::-1])

    plt.xlabel("Confidence")
    plt.title("Top Association Rules by Confidence")

    path = FIGURES_DIR / "top_rules_by_confidence.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    return path

def generate_html_report(image_paths: list[Path]) -> Path:
    html_path = REPORT_DIR / "market_basket_report.html"

    rules = pd.read_csv(EXPORT_DIR / "association_rules.csv")

    total_rules = len(rules)
    avg_lift = round(rules["lift"].mean(), 2)
    avg_confidence = round(rules["confidence"].mean(), 3)
    avg_support = round(rules["support"].mean(), 4)

    top_lift_rule = rules.sort_values("lift", ascending=False).iloc[0]
    top_support_rule = rules.sort_values("pair_count", ascending=False).iloc[0]

    top_lift_label = f"{top_lift_rule['product_1_name']} → {top_lift_rule['product_2_name']}"
    top_support_label = f"{top_support_rule['product_1_name']} + {top_support_rule['product_2_name']}"

    descriptions = {
        "top_association_rules": "Ranks the product association rules with the highest lift, highlighting the strongest product relationships.",
        "lift_distribution": "Shows the overall distribution of lift values across association rules.",
        "support_vs_confidence": "Compares rule frequency and rule strength to identify the most actionable rules.",
        "cross_sell_opportunities": "Highlights product combinations with strong cross-sell potential based on confidence and lift.",
        "product_network": "Network graph showing relationships between strongly associated products.",
        "rule_quality_quadrant": "Compares confidence and lift while sizing rules by pair frequency to highlight the most actionable associations.",
        "top_rules_by_confidence": "Ranks association rules by confidence to identify the strongest conditional product recommendations.",
    }

    cards_html = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Association Rules</div>
            <div class="kpi-value">{total_rules:,}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Average Lift</div>
            <div class="kpi-value">{avg_lift}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Average Confidence</div>
            <div class="kpi-value">{avg_confidence}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Average Support</div>
            <div class="kpi-value">{avg_support}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Top Lift Rule</div>
            <div class="kpi-value small">{top_lift_label}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Most Frequent Pair</div>
            <div class="kpi-value small">{top_support_label}</div>
        </div>
    </div>
    <h2 class="section-title">Key Insights</h2>

    <div class="kpi-grid">

    <div class="kpi-card">
    <div class="kpi-label">Strongest Product Association</div>
    <div class="kpi-value small">
    Icelandic Style Skyr Blueberry Non-fat Yogurt → Non Fat Raspberry Yogurt
    </div>
    </div>

    <div class="kpi-card">
    <div class="kpi-label">Most Frequent Basket Pair</div>
    <div class="kpi-value small">
    Organic Yellow Onion + Organic Garlic
    </div>
    </div>

    <div class="kpi-card">
    <div class="kpi-label">Typical Confidence Range</div>
    <div class="kpi-value small">
    0.08 – 0.15
    </div>
    </div>

    <div class="kpi-card">
    <div class="kpi-label">Typical Lift Range</div>
    <div class="kpi-value small">
    2 – 10+
    </div>
    </div>

    </div>
    """

    ordered_chart_keys = [
        "top_association_rules",
        "lift_distribution",
        "support_vs_confidence",
        "cross_sell_opportunities",
        "product_network",
        "rule_quality_quadrant",
        "top_rules_by_confidence",
    ]

    image_map = {path.stem: path for path in image_paths}

    image_blocks = []
    for chart_key in ordered_chart_keys:
        path = image_map.get(chart_key)
        if not path:
            continue

        title = chart_key.replace("_", " ").title()
        relative_path = f"figures/{path.name}"
        description = descriptions.get(chart_key, "Market basket analysis visualization.")

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
    <title>Market Basket Analysis Report</title>
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
            <h1>Market Basket Analysis Report</h1>
            <p>
                This report presents association rule mining results built from the Instacart Market Basket dataset.
                Product co-occurrence patterns were analyzed from filtered baskets in DuckDB, exported to CSV,
                and visualized with Python and Matplotlib to identify frequently bought together products and
                cross-sell opportunities.
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
            Retail Analytic Platform · Market Basket Analysis
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
    <strong>Support</strong> measures how frequently a product pair appears in all orders.
    Higher support indicates more common combinations.
    </p>

    <p>
    <strong>Confidence</strong> measures how often product B is purchased when product A
    is already in the basket.
    </p>

    <p>
    <strong>Lift</strong> measures how much more likely the two products are purchased
    together compared to random chance. Lift values above 1 indicate a positive
    association.
    </p>
</body>
</html>
"""

    html_path.write_text(html_content, encoding="utf-8")
    return html_path

def main() -> None:
    generated_files = []

    generated_files.append(plot_top_association_rules())
    generated_files.append(plot_lift_distribution())
    generated_files.append(plot_support_confidence())
    generated_files.append(plot_cross_sell())
    generated_files.append(plot_product_network())
    generated_files.append(plot_rule_quality_quadrant())
    generated_files.append(plot_top_rules_by_confidence())

    html_report = generate_html_report(generated_files)

    print("Visualizations generated:")
    for file_path in generated_files:
        print(f"- {file_path}")

    print(f"\nHTML report generated:\n- {html_report}")


if __name__ == "__main__":
    main()