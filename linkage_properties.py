def compute_linkage_properties(L1, L2, L3, L4, valid_steps=None, total_steps=None):

    tol = 1e-6

    links = [L1, L2, L3, L4]
    s = min(links)
    l = max(links)

    # remaining two
    temp = links.copy()
    temp.remove(s)
    temp.remove(l)
    p, q = temp

    grashof_index = (p + q) - (s + l)

    if grashof_index > tol:
        linkage_type = "Grashof"
    elif abs(grashof_index) <= tol:
        linkage_type = "Change-Point"
    else:
        linkage_type = "Non-Grashof"

    if linkage_type == "Grashof":

        if abs(L1 - s) < tol:
            # Ground shortest → Double crank
            input_type = "Crank"
            output_type = "Crank"

        elif abs(L2 - s) < tol:
            input_type = "Crank"
            output_type = "Rocker"

        elif abs(L4 - s) < tol:
            input_type = "Rocker"
            output_type = "Crank"

        else:
            input_type = "Rocker"
            output_type = "Rocker"

    else:
        input_type = "Rocker"
        output_type = "Rocker"



    # Validity index
    validity_index = None
    if valid_steps is not None and total_steps is not None:
        validity_index = (valid_steps / total_steps) * 100

    return {
        "Linkage Type": linkage_type,
        "Input Type": input_type,
        "Output Type": output_type,
        "Grashof Index": round(grashof_index, 4),
        "Validity Index": round(validity_index, 2) if validity_index else None
    }
