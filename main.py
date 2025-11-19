import os
from pdf_extractor import extract_text, clean_text
from llm_main import extract_supplier_data
from supplier_compare import build_comparison_table, compute_tco, recommend_best_supplier
from currency_ex import convert_to_eur  

PDF_DIR = "llm_innovation_task_pdf_samples/sample"

print(f"Scanning folder: {PDF_DIR}")
pdfs = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
print(f"Found {len(pdfs)} PDF files.\n")

all_results = []



for pdf in pdfs:
    path = os.path.join(PDF_DIR, pdf)
    print(f"Processing: {pdf}")

    try:
        raw_text = extract_text(path)
        cleaned_text = clean_text(raw_text)

        # LLM extraction → structured JSON
        data = extract_supplier_data(cleaned_text)

        all_results.append({"file": pdf, "data": data})
        print("  ✓ Extraction successful")

    except Exception as e:
        print("  ✗ Extraction failed:", e)
        all_results.append({"file": pdf, "error": str(e)})


# 2) PRINT RAW RESULTS
# ----------------------------------------------------------
print("\n--- RAW EXTRACTION RESULTS ---")
for r in all_results:
    print(r)


#NORMALIZE CURRENCY 
for entry in all_results:
    if "error" in entry:
        continue

    data = entry["data"]
    currency = data.get("currency", "EUR")
    yby = data.get("year_by_year_pricing", [])

 
    prices = []
    for row in yby:
        try:
            prices.append(float(row["price"]))
        except:
            pass

    avg_price = sum(prices) / len(prices) if prices else None

    # Convert to EUR
    data["avg_price_eur"] = convert_to_eur(avg_price, currency, data) if avg_price else None


    tooling = data.get("tooling_costs")
    data["tooling_eur"] = convert_to_eur(tooling, currency, data) if tooling else 0



print("\n COMPARISON TABLE")
comparison_df = build_comparison_table(all_results)
print(comparison_df)



print("\n TCO TABLE")
tco_df = compute_tco(all_results)
print(tco_df)


best_supplier, recommendation_text = recommend_best_supplier(tco_df)
print("\nRECOMMENDATION ")
print(recommendation_text)



print("\nProcessing complete.\n")
