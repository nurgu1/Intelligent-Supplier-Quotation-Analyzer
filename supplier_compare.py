import pandas as pd

def build_comparison_table(results):

    rows = []
    for entry in results:
        data = entry["data"]

        # average unit price across years if exists
        if data["year_by_year_pricing"]:
            avg_price = sum(float(y["price"]) for y in data["year_by_year_pricing"]) / len(data["year_by_year_pricing"])
        else:
            avg_price = None

        rows.append({
            "Supplier": data["supplier_name"],
            "Currency": data["currency"],
            "MOQ": data["MOQ"],
            "Tooling Costs": data["tooling_costs"],
            "Delivery Terms": data["delivery_terms"],
            "Payment Terms": data["payment_terms"],
            "Lead Time": data["delivery_time"],
            "Validity": data["validity_period"],
            "Avg Unit Price (across years)": avg_price,
        })

    return pd.DataFrame(rows)
    
def compute_tco(results):
    tco_rows = []

    for entry in results:
        file_name = entry["file"]
        data = entry["data"]

        # Estimate total spend (avg price * volume for years provided)
        total_product_cost = 0
        for y in data["year_by_year_pricing"]:
            try:
                total_product_cost += float(y["price"]) * float(y["volume"].replace(",", "").replace(".", ""))
            except:
                pass

        tooling = data["tooling_costs"] or 0

        tco = total_product_cost + tooling

        tco_rows.append({
            "Supplier": data["supplier_name"],
            "Total Product Cost": total_product_cost,
            "Tooling Cost": tooling,
            "TCO (Total Cost of Ownership)": tco,
        })

    return pd.DataFrame(tco_rows)


def recommend_best_supplier(tco_df):
    best = tco_df.sort_values("TCO (Total Cost of Ownership)").iloc[0]
    explanation = (
        f"Supplier **{best['Supplier']}** is recommended because it has the lowest "
        f"Total Cost of Ownership (TCO) of **{best['TCO (Total Cost of Ownership)']:.2f}**, "
        f"including tooling and multi-year product pricing."
    )
    return best, explanation
