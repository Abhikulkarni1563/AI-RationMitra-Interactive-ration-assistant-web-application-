import re
from models import Commodity, UserRation, db
from extensions import db

# -------------------- NLP Parser --------------------
def parse_ration_request(user_input):
    """
    Extract quantities and commodity names from user input using NLP.
    Example: "5kg rice and 2kg sugar" -> [('rice', 5), ('sugar', 2)]
    """
    pattern = r'(\d+)\s*(kg|liters)?\s*(\w+)'  # Match "5kg rice", "2 liters sugar"
    matches = re.findall(pattern, user_input.lower())

    orders = []
    for match in matches:
        quantity, _, item = match
        orders.append((item.strip(), int(quantity)))
    return orders

# -------------------- Stock Management --------------------
def update_stock(user_id, orders):
    """
    Deduct stock for requested commodities and validate against user quotas.
    """
    response = []

    for item, quantity in orders:
        commodity = Commodity.query.filter_by(name=item).first()

        if not commodity or commodity.stock < quantity:
            response.append(f"❌ Insufficient stock for {item}. Available: {commodity.stock if commodity else 0}kg.")
            continue

        # Fetch user ration quota
        user_ration = UserRation.query.filter_by(user_id=user_id, commodity=item).first()
        if user_ration:
            if user_ration.consumed + quantity > user_ration.quota_limit:
                response.append(f"⚠️ Exceeds {item} quota. Limit: {user_ration.quota_limit}kg.")
                continue
            user_ration.consumed += quantity
        else:
            response.append(f"⚠️ No quota assigned for {item}.")
            continue

        # Deduct stock
        commodity.stock -= quantity
        db.session.commit()
        response.append(f"✅ {quantity}kg of {item} dispensed. Remaining: {commodity.stock}kg.")

    return " | ".join(response)
