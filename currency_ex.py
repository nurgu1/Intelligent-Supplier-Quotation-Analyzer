
def get_conversion_rate(supplier_data):
    """
    Detect if PDF text includes an explicit exchange rate.
    Example in TG Display Japan PDF:
        "Exchange Rate USD/EUR 1.18"
    If found, use it.
    If not found, use a safe fallback.
    """
    notes = (supplier_data.get("other_notes") or "").lower()
    
    if "usd/eur" in notes:
        try:
            part = notes.split("usd/eur")[1].strip()
            rate = float(part.split()[0])
            return rate
        except:
            pass

  
    return 1.18


def convert_to_eur(amount, currency, supplier_data):
    """
    Convert a price into EUR using detected exchange rate.
    - If currency is EUR → return amount unchanged.
    - If USD → convert using USD/EUR rate.
    """
    if amount is None:
        return None
    
    currency = (currency or "").upper()

    if currency == "EUR":
        return float(amount)
    
    if currency == "USD":
        usd_per_eur = get_conversion_rate(supplier_data)  
        eur_per_usd = 1 / usd_per_eur                      
        return float(amount) * eur_per_usd

    return float(amount)
