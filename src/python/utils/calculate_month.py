def calculate_month(elapsed_months: int, start_month: int) -> str:
    """
    Calculates the resulting month after a given number of elapsed months,
    starting from an initial month.

    Args:
        elapsed_months (int): The number of months that have passed.
        start_month (str): The name of the starting month (e.g., "January", "February", etc.).

    Returns:
        str: The name of the resulting month.
    """
    if start_month < 1 or start_month > 12:
        return "invalid"

    months = ["january", "february", "march", "april", "may", "june",
              "july", "august", "september", "october", "november", "december"]

    end_index = (start_month + elapsed_months) % 12
    return months[end_index-1]