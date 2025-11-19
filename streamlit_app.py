import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from pdf_extractor import extract_text, clean_text
from llm_main import extract_supplier_data
from currency_ex import convert_to_eur
from scoring import compute_lead_weeks, simple_weighted_score
load_dotenv()

st.set_page_config(page_title="Supplier Quotation Analyzer", layout="wide")
st.title("📄 Intelligent Supplier Quotation Analyzer")

def get_supplier_name(entry, d):
    return (
        d.get("supplier_name")
        or d.get("client_name")
        or entry["file"]
    )

uploaded_files = st.file_uploader(
    "Upload supplier quotation PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

all_results = []

if uploaded_files:
    st.header("Extracted Data")

    for pdf in uploaded_files:
        st.subheader(pdf.name)

        raw = extract_text(pdf)
        cleaned = clean_text(raw)

        try:
            data = extract_supplier_data(cleaned)
        except Exception as e:
            st.error(f"Extraction failed: {e}")
            continue

        all_results.append({"file": pdf.name, "data": data})
        st.json(data)

    for entry in all_results:
        d = entry["data"]
        curr = d.get("currency", "EUR")
        rows = d.get("year_by_year_pricing", [])

        prices = []
        for r in rows:
            try:
                prices.append(float(r["price"]))
            except:
                pass

        avg_price = sum(prices) / len(prices) if prices else None
        d["avg_price_eur"] = convert_to_eur(avg_price, curr, d) if avg_price else None
        d["tooling_eur"] = convert_to_eur(d.get("tooling_costs"), curr, d) if d.get("tooling_costs") else 0

    st.header("Supplier Comparison")

    comp = []
    for entry in all_results:
        d = entry["data"]
        supplier = get_supplier_name(entry, d)
        curr = d.get("currency", "EUR")

        orig_prices = []
        for y in d.get("year_by_year_pricing", []):
            try:
                orig_prices.append(float(y["price"]))
            except:
                pass

        avg_orig = sum(orig_prices) / len(orig_prices) if orig_prices else None

        comp.append({
            "Supplier": supplier,
            "Currency": curr,
            "Avg Price (Original)": avg_orig,
            "Avg Price (EUR)": d["avg_price_eur"],
            "Tooling (EUR)": d["tooling_eur"],
            "MOQ": d.get("MOQ"),
            "Delivery Terms": d.get("delivery_terms"),
            "Lead Time": d.get("delivery_time"),
            "Payment Terms": d.get("payment_terms")
        })

    comparison_df = pd.DataFrame(comp)
    st.dataframe(comparison_df, use_container_width=True)

    st.header("Total Cost of Ownership (EUR)")

    tco_rows = []
    for entry in all_results:
        d = entry["data"]
        curr = d.get("currency", "EUR")
        supplier = get_supplier_name(entry, d)

        total_cost = 0
        for r in d.get("year_by_year_pricing", []):
            try:
                price_eur = convert_to_eur(float(r["price"]), curr, d)
                volume = float(r["volume"].replace(",", "").replace(".", ""))
                total_cost += price_eur * volume
            except:
                pass

        tooling = d["tooling_eur"]
        tco = total_cost + tooling

        tco_rows.append({
            "Supplier": supplier,
            "Product Cost (EUR)": total_cost,
            "Tooling (EUR)": tooling,
            "Total TCO (EUR)": tco
        })

    tco_df = pd.DataFrame(tco_rows)
    st.dataframe(tco_df, use_container_width=True)

    st.header("Final Weighted Scoring")

    scoring = []
    all_tcos = tco_df["Total TCO (EUR)"].tolist()

    all_leads = []
    for entry in all_results:
        w = compute_lead_weeks(entry["data"].get("delivery_time"))
        if w:
            all_leads.append(w)
    if not all_leads:
        all_leads = [1, 2]

    for entry in all_results:
        d = entry["data"]
        supplier = get_supplier_name(entry, d)

        row = tco_df[tco_df["Supplier"] == supplier]
        if row.empty:
            continue
        tco = row["Total TCO (EUR)"].values[0]

        lead_weeks = compute_lead_weeks(d.get("delivery_time")) or max(all_leads)

        comm = 0
        if "90" in str(d.get("payment_terms")):
            comm += 1
        if str(d.get("MOQ")).replace(",", "").isdigit() and int(str(d.get("MOQ")).replace(",", "")) < 7000:
            comm += 1
        if d.get("delivery_terms"):
            comm += 1

        commercial_score = comm / 3

        score = simple_weighted_score(
            tco, all_tcos,
            lead_weeks, all_leads,
            commercial_score
        )

        scoring.append({
            "Supplier": supplier,
            "TCO (EUR)": round(tco, 2),
            "Lead (weeks)": lead_weeks,
            "Commercial Score": round(commercial_score, 2),
            "Final Score": round(score, 4)
        })

    scoring_df = pd.DataFrame(scoring).sort_values("Final Score", ascending=False)
    st.dataframe(scoring_df, use_container_width=True)

    best = scoring_df.iloc[0]

    st.success(
        f"### 🏆 Final Recommendation: **{best['Supplier']}**\n"
        f"Score: **{best['Final Score']}**\n\n"
        f"- TCO: {best['TCO (EUR)']:.2f} EUR\n"
        f"- Lead Time: {best['Lead (weeks)']} weeks\n"
        f"- Commercial Score: {best['Commercial Score']}\n"
    )
