"""Generate the Topic 47 submission deck from verified project outputs."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
DECK = ROOT / "presentation" / "Topic47_Presentation.pdf"
BG, FG, MUTED, ACCENT = "#111827", "#f9fafb", "#cbd5e1", "#38bdf8"


def page(title: str, number: int) -> tuple[plt.Figure, plt.Axes]:
    figure, axis = plt.subplots(figsize=(13.333, 7.5), facecolor=BG)
    axis.set_facecolor(BG)
    axis.axis("off")
    axis.text(0.06, 0.91, title, color=FG, fontsize=25, fontweight="bold", transform=axis.transAxes)
    axis.text(0.06, 0.04, "Topic 47 · Kazakhstan OSM POI Analytics", color=MUTED, fontsize=9, transform=axis.transAxes)
    axis.text(0.94, 0.04, str(number), color=MUTED, fontsize=9, ha="right", transform=axis.transAxes)
    return figure, axis


def bullets(axis: plt.Axes, items: list[str], y: float = 0.75, size: int = 16) -> None:
    for item in items:
        axis.text(0.09, y, "• " + textwrap.fill(item, 88), color=FG, fontsize=size, va="top", transform=axis.transAxes, linespacing=1.5)
        y -= 0.12 + 0.025 * (len(item) // 88)


def save(pdf: PdfPages, figure: plt.Figure) -> None:
    pdf.savefig(figure, facecolor=figure.get_facecolor(), bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    quality = json.loads((OUTPUTS / "quality_report.json").read_text(encoding="utf-8"))
    manifest = json.loads((OUTPUTS / "manifest.json").read_text(encoding="utf-8"))
    hypotheses = json.loads((OUTPUTS / "hypotheses.json").read_text(encoding="utf-8"))
    clusters = json.loads((OUTPUTS / "clustering_report.json").read_text(encoding="utf-8"))
    cities = pd.read_csv(OUTPUTS / "city_stats.csv")
    benchmark = pd.read_csv(OUTPUTS / "benchmark.csv")
    metrics = pd.read_csv(OUTPUTS / "gpu_model_metrics.csv")
    assert quality["rows"] == quality["unique_osm_keys"]
    assert len(cities) == 3 and len(benchmark) == 3 and len(metrics) == 3
    DECK.parent.mkdir(exist_ok=True)

    with PdfPages(DECK) as pdf:
        figure, axis = plt.subplots(figsize=(13.333, 7.5), facecolor=BG)
        axis.set_facecolor(BG)
        axis.axis("off")
        axis.text(0.08, 0.68, "OpenStreetMap Kazakhstan", color=FG, fontsize=34, fontweight="bold", transform=axis.transAxes)
        axis.text(0.08, 0.57, "Points of Interest Analytics", color=ACCENT, fontsize=28, transform=axis.transAxes)
        axis.text(0.08, 0.40, "AAI-2605M · Topic 47", color=FG, fontsize=18, transform=axis.transAxes)
        axis.text(0.08, 0.33, "Student: [replace with your name and ID]", color=MUTED, fontsize=14, transform=axis.transAxes)
        axis.text(0.08, 0.27, "Repository: [add your GitHub URL before submission]", color=MUTED, fontsize=14, transform=axis.transAxes)
        axis.text(0.08, 0.08, "Data: © OpenStreetMap contributors, ODbL 1.0 · Geofabrik · Kazakhstan BNS", color=MUTED, fontsize=10, transform=axis.transAxes)
        save(pdf, figure)

        figure, axis = page("Problem and objectives", 2)
        bullets(axis, [
            "Analyze the distribution and composition of mapped OpenStreetMap points of interest across Kazakhstan.",
            "Compare 20 current first-level regions and the three standalone city-regions: Astana, Almaty city, and Shymkent.",
            "Calculate population- and area-normalized indicators, identify spatial clusters, and demonstrate reproducible data engineering.",
            "Deliver an interactive dashboard, normalized SQLite database, statistical analysis, and an unsupervised neighbourhood-profile extension.",
        ])
        save(pdf, figure)

        figure, axis = page("Data and processing pipeline", 3)
        bullets(axis, [
            "Input: Geofabrik Kazakhstan PBF; population snapshot: Kazakhstan Bureau of National Statistics, 2026-10-01.",
            "Osmium filters amenity, shop, tourism, and leisure tags; each OSM node, way, or relation retains a type-qualified key.",
            "Representative points and 20 current ADM1 OSM polygons support spatial assignment; unmatched POIs remain visible in quality reporting.",
            "Processed Parquet, GeoJSON, SQLite, figures, DBSCAN outputs, and model artifacts are bundled for reproducible dashboard use.",
        ])
        save(pdf, figure)

        figure, axis = page("Dataset coverage and quality", 4)
        values = [quality["rows"], 20, manifest["population_total"], quality["missing_region_count"]]
        labels = ["Mapped POIs", "ADM1 regions", "Population", "Unmatched POIs"]
        positions = [0.08, 0.31, 0.54, 0.77]
        for x, label, value in zip(positions, labels, values):
            axis.text(x, 0.62, label, color=MUTED, fontsize=14, transform=axis.transAxes)
            axis.text(x, 0.50, f"{value:,}", color=ACCENT, fontsize=28, fontweight="bold", transform=axis.transAxes)
        bullets(axis, [
            f"Missing names: {quality['missing_name_count']:,}; invalid coordinates: {quality['invalid_coordinates']}; duplicate OSM keys: {quality['duplicate_osm_keys']}.",
            "IQR outliers are evaluated but not automatically deleted. OSM mapped features are not a complete real-world facility census.",
        ], y=0.30, size=14)
        save(pdf, figure)

        figure, axis = page("National POI composition", 5)
        chart = figure.add_axes([0.09, 0.18, 0.82, 0.58], facecolor=BG)
        counts = pd.Series(quality["category_counts"]).sort_values(ascending=True)
        chart.barh(counts.index, counts.values, color=ACCENT)
        chart.tick_params(colors=FG, labelsize=10)
        chart.spines[:].set_visible(False)
        chart.grid(axis="x", alpha=0.15, color=FG)
        chart.set_xlabel("Mapped POIs", color=FG)
        chart.set_title("OSM feature counts by broad category", color=FG, loc="left", pad=12)
        save(pdf, figure)

        figure, axis = page("Standalone city-region comparison", 6)
        chart = figure.add_axes([0.08, 0.21, 0.55, 0.55], facecolor=BG)
        chart.bar(cities["region_name"], cities["per_100k"], color=["#38bdf8", "#60a5fa", "#f59e0b"])
        chart.tick_params(colors=FG, labelrotation=15)
        chart.spines[:].set_visible(False)
        chart.grid(axis="y", alpha=0.15, color=FG)
        chart.set_ylabel("Mapped POIs per 100K residents", color=FG)
        axis.text(0.69, 0.68, "Key results", color=ACCENT, fontsize=16, fontweight="bold", transform=axis.transAxes)
        bullets(axis, [
            "Almaty city: 23,460 POIs; 980.7 per 100K.",
            "Astana city: 9,411 POIs; 551.3 per 100K.",
            "Shymkent city: 3,256 POIs; 246.5 per 100K.",
        ], y=0.60, size=13)
        save(pdf, figure)

        figure, axis = page("Exploratory statistics and DBSCAN", 7)
        h1, h2 = hypotheses
        bullets(axis, [
            f"H1 category distributions: χ²(18) = {h1['chi2']:.2f}, p = {h1['p_value']:.2e}, Cramér's V = {h1['cramers_v']:.3f}. The city-region mixes differ, with a small association.",
            f"H2 healthcare nearest-neighbour distances: Mann–Whitney U = {h2['u']:,.0f}, p = {h2['p_value']:.4f}; medians are {h2['median_astana_km']:.3f} km in Astana and {h2['median_almaty_km']:.3f} km in Almaty city.",
            f"DBSCAN (haversine; ε=0.5 km; min_samples=8): Astana {clusters['astana']['clusters']} clusters, Almaty city {clusters['almaty_city']['clusters']} clusters, Shymkent {clusters['shymkent']['clusters']} clusters.",
            "Almaty city DBSCAN uses a 12,000-point cap and is exploratory. Spatial dependence limits causal interpretation of p-values.",
        ], size=14)
        save(pdf, figure)

        figure, axis = page("Reproducible aggregation benchmark", 8)
        chart = figure.add_axes([0.10, 0.20, 0.38, 0.55], facecolor=BG)
        chart.bar(benchmark["approach"], benchmark["time_seconds"], color=ACCENT)
        chart.tick_params(colors=FG)
        chart.spines[:].set_visible(False)
        chart.set_ylabel("Seconds", color=FG)
        chart.set_title("Runtime", color=FG)
        chart.grid(axis="y", alpha=0.15, color=FG)
        chart2 = figure.add_axes([0.56, 0.20, 0.38, 0.55], facecolor=BG)
        chart2.bar(benchmark["approach"], benchmark["peak_process_rss_mib"], color="#60a5fa")
        chart2.tick_params(colors=FG)
        chart2.spines[:].set_visible(False)
        chart2.set_ylabel("MiB", color=FG)
        chart2.set_title("Peak process RSS", color=FG)
        chart2.grid(axis="y", alpha=0.15, color=FG)
        axis.text(0.06, 0.08, "All three implementations matched the SQLite aggregate baseline. These are single-run environmental measurements.", color=MUTED, fontsize=11, transform=axis.transAxes)
        save(pdf, figure)

        figure, axis = page("Unsupervised neighbourhood profiles", 9)
        chart = figure.add_axes([0.10, 0.20, 0.56, 0.55], facecolor=BG)
        chart.bar(metrics["method"], metrics["mse"], color=["#94a3b8", "#60a5fa", "#38bdf8"])
        chart.tick_params(colors=FG, labelrotation=12)
        chart.spines[:].set_visible(False)
        chart.set_ylabel("Test MSE", color=FG)
        chart.grid(axis="y", alpha=0.15, color=FG)
        bullets(axis, [
            "2 km urban grid cells; 10 POI-category inputs; four-dimensional latent embedding.",
            "GPU autoencoder MSE: 0.12963 versus PCA: 0.17093 (24.2% MSE improvement).",
            "Unsupervised reconstruction—not POI prediction or DBSCAN.",
        ], y=0.68, size=12)
        save(pdf, figure)

        figure, axis = page("Conclusions, limitations, and submission", 10)
        bullets(axis, [
            "The delivered dashboard enables regional, city-region, geographic-cluster, SQL, and model-profile exploration from precomputed artifacts.",
            "Mapped counts must not be interpreted as the complete real-world stock of facilities; OSM coverage varies by place and time.",
            "Only the three standalone city-regions support valid city-level per-capita comparison in this dataset.",
            "Submission: GitHub repository URL, this report, and this PDF deck. Replace title-slide placeholders before upload.",
        ], size=14)
        axis.text(0.09, 0.15, "Sources: Geofabrik · OpenStreetMap / ODbL · Kazakhstan BNS · Osmium · GeoPandas", color=MUTED, fontsize=10, transform=axis.transAxes)
        save(pdf, figure)

    print(f"Created {DECK}")


if __name__ == "__main__":
    main()
