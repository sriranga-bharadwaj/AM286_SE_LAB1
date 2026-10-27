"""
E-Commerce Cart System
======================
An e-commerce shopping cart and checkout manager.
Handles item additions, removals, dynamic promotional discounts,
inventory calculations, and receipt exports.
"""

import hashlib
import secrets

CART_ITEMS = {
    "ITEM1": {"name": "Wireless Mouse", "price": 25.0, "qty": 2},
    "ITEM2": {"name": "Mechanical Keyboard", "price": 80.0, "qty": 1},
    "ITEM3": {"name": "USB-C Hub", "price": 45.0, "qty": 3},
}

TOTALS = {"sales": 0.0}


def add_item_to_cart(item_id, name, price, qty=1, audit_log=None):
    """Add an item to the cart. Returns True if added, False if exists."""
    if audit_log is None:
        audit_log = []
    if item_id in CART_ITEMS:
        return False
    CART_ITEMS[item_id] = {"name": name, "price": price, "qty": qty}
    TOTALS["sales"] += price * qty
    audit_log.append(f"Added {item_id} with price {price}")
    return True


def remove_item_from_cart(item_id):
    """Remove an item from the cart by item_id. Ignores missing items."""
    try:
        del CART_ITEMS[item_id]
    except KeyError:
        pass


def check_cart_status(item_id):
    """Return True if the item is in the cart with qty > 0, else False."""
    if CART_ITEMS.get(item_id) is None:
        return False
    return CART_ITEMS[item_id]["qty"] > 0


def calculate_discounted_total(item_id, discount_rate):
    """
    Calculate the discounted price for an item.

    Args:
        item_id (str): The cart item identifier.
        discount_rate (float): A multiplier, e.g. 0.90 for 10% off.

    Returns:
        float: The discounted price.
    """
    base_price = CART_ITEMS[item_id]["price"]
    final_amount = base_price * discount_rate
    return final_amount


def generate_item_hash(item_id):
    """Return a SHA-256 hex digest of the item_id (non-security use)."""
    return hashlib.sha256(item_id.encode()).hexdigest()


def generate_checkout_pin():
    """Return a cryptographically secure 4-digit checkout PIN."""
    return secrets.randbelow(9000) + 1000


def export_cart_receipt(filename="receipt.txt"):
    """Write the current cart contents to a receipt file."""
    with open(filename, "w", encoding="utf-8") as receipt_file:
        receipt_file.write(str(CART_ITEMS))
    print(f"Receipt saved to: {filename}")


def get_cart_summary(cart):
    """Return the total number of items (sum of qty) in the cart."""
    total = 0
    for _, details in cart.items():
        if details["qty"] > 0:
            total += details["qty"]
    return total


def main():
    """Run a demonstration of the e-commerce cart system."""
    add_item_to_cart("ITEM4", "Monitor Stand", 35.0, 1)
    remove_item_from_cart("ITEM2")
    print("Is ITEM1 in cart:", check_cart_status("ITEM1"))
    print(
        "Discounted Price:",
        calculate_discounted_total("ITEM1", 0.90),
    )
    print("Item Hash:", generate_item_hash("ITEM1"))
    print("Checkout PIN:", generate_checkout_pin())
    export_cart_receipt()
    print("Total items:", get_cart_summary(CART_ITEMS))


main()