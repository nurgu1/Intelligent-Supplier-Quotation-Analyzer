def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 1
    return (max_val - value) / (max_val - min_val)

def compute_lead_weeks(lead_time_str):
    if not lead_time_str:
        return None

    txt = lead_time_str.lower().replace("~", "").replace("–", "-")


    try:
        if "-" in txt:
            a, b = txt.split("-")[0:2]
            return (float(a) + float(b.split()[0])) / 2
        else:
            return float(txt.split()[0])
    except:
        return None


def simple_weighted_score(supplier_tco, all_tcos, lead_weeks, all_leads, commercial_score):
    min_tco, max_tco = min(all_tcos), max(all_tcos)
    min_lead, max_lead = min(all_leads), max(all_leads)

    tco_score = normalize(supplier_tco, min_tco, max_tco)
    lead_score = normalize(lead_weeks, min_lead, max_lead)

    final_score = (
        0.50 * tco_score +
        0.25 * lead_score +
        0.15 * commercial_score 
    )
    return final_score
