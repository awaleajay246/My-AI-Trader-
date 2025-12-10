def get_scenario(pcr, ce_oi, pe_oi):
    if pcr > 1.3 and pe_oi > ce_oi:
        return 1
    elif pcr > 1.1:
        return 2
    elif pcr > 1.0:
        return 3
    elif pcr < 0.7 and ce_oi > pe_oi:
        return 4
    elif pcr < 0.9:
        return 5
    elif pcr < 1.0:
        return 6
    else:
        return 9  # neutral
