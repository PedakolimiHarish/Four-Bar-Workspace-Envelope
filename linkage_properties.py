def compute_linkage_properties(L1, L2, L3, L4):

    tol = 1e-6
    links = [L1, L2, L3, L4]

    # ----------------------------------
    # 1️⃣ Assembly Validity Check
    # ----------------------------------
    if max(links) > sum(links) - max(links):
        return {
            "Assembly": "Invalid",
            "Grashof Class": "-",
            "Mechanism Type": "Cannot Assemble",
            "Input Type": "-",
            "Output Type": "-"
        }

    # ----------------------------------
    # 2️⃣ Special Symmetry Cases
    # ----------------------------------
    special = None

    if abs(L1 - L3) < tol and abs(L2 - L4) < tol:
        special = "Parallelogram"

    elif abs(L1 - L2) < tol and abs(L3 - L4) < tol:
        special = "Kite Linkage"

    elif abs(L1 - L4) < tol and abs(L2 - L3) < tol:
        special = "Rhomboid (Galloway)"

    # ----------------------------------
    # 3️⃣ Grashof Classification
    # ----------------------------------
    s = min(links)
    l = max(links)

    temp = links.copy()
    temp.remove(s)
    temp.remove(l)
    p, q = temp

    GI = (p + q) - (s + l)

    if GI > tol:
        grashof_class = "Grashof"
    elif GI < -tol:
        grashof_class = "Non-Grashof"
    else:
        grashof_class = "Change-Point"

    # ----------------------------------
    # 4️⃣ Mechanism Type
    # ----------------------------------
    mechanism = "-"
    input_type = "-"
    output_type = "-"

    if special:
        mechanism = special
        input_type = "Crank"
        output_type = "Crank"

    elif grashof_class == "Non-Grashof":
        mechanism = "Double Rocker"
        input_type = "Rocker"
        output_type = "Rocker"

    else:
        if abs(L1 - s) < tol:
            mechanism = "Double Crank"
            input_type = "Crank"
            output_type = "Crank"

        elif abs(L2 - s) < tol:
            mechanism = "Crank-Rocker"
            input_type = "Crank"
            output_type = "Rocker"

        elif abs(L4 - s) < tol:
            mechanism = "Rocker-Crank"
            input_type = "Rocker"
            output_type = "Crank"

        else:
            mechanism = "Double Rocker"
            input_type = "Rocker"
            output_type = "Rocker"

        if grashof_class == "Change-Point":
            mechanism += " (Change-Point)"

    return {
        "Assembly": "Valid",
        "Grashof Class": grashof_class,
        "Mechanism Type": mechanism,
        "Input Type": input_type,
        "Output Type": output_type
    }