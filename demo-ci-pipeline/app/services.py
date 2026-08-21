def calculate_discount(price: float, discount_percentage: float) -> float:
    """Return the discounted price for a given percentage discount."""
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError("discount_percentage must be between 0 and 100")
    return price - (price * discount_percentage / 100)


def format_user_data(user_tuple):
    """Convert a database tuple (id, name) into a dictionary."""
    user_id, name = user_tuple
    return {"id": user_id, "name": name}
