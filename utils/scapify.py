def int_to_gp(num):
    if num >= 10 ** 9:  # Billions
        return f"{num / 10 ** 9:.2f}B"
    elif num >= 10 ** 6:  # Millions
        return f"{num / 10 ** 6:.2f}M"
    elif num >= 10 ** 3:  # Thousands
        return f"{num / 10 ** 3:.2f}K"
    else:
        return str(num) + " gp"

def gp_to_int(gp_str):
    gp_str = gp_str.strip().lower()  # Remove any extra spaces and convert to lowercase

    if gp_str.endswith("b"):  # Billions
        return int(float(gp_str[:-1]) * 10 ** 9)
    elif gp_str.endswith("m"):  # Millions
        return int(float(gp_str[:-1]) * 10 ** 6)
    elif gp_str.endswith("k"):  # Thousands
        return int(float(gp_str[:-1]) * 10 ** 3)
    elif gp_str.endswith("gp"):  # Just gp, no scaling
        return int(gp_str[:-2].strip())
    else:
        # If the input is just a number (no unit), directly convert
        return int(gp_str)
