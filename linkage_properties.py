# --------------------------------------------------
# linkage_properties.py
#
# This module analyzes the geometric properties of a
# four-bar linkage based only on its link lengths.
#
# It classifies the mechanism according to classical
# mechanism theory.
#
# The function determines:
# 1) Whether the linkage can physically assemble
# 2) Its Grashof class (Grashof / Non-Grashof / Change-Point)
# 3) The specific mechanism type
# 4) Expected motion type of input and output links
#
# This module does NOT solve the mechanism motion.
# It only performs classification based on link lengths.
# --------------------------------------------------


# --------------------------------------------------
# Classifies the four-bar linkage based on link lengths.
#
# Determines:
# - Assembly validity
# - Grashof class
# - Mechanism type
# - Expected input/output motion type
# --------------------------------------------------

def compute_linkage_properties(L1, L2, L3, L4):

    # Small tolerance used for floating-point comparisons
    tol = 1e-6

    # Store link lengths in a list for easier processing
    links = [L1, L2, L3, L4]

    # ----------------------------------
    # 1️⃣ Assembly Validity Check
    # ----------------------------------
    #
    # A four-bar linkage can only exist if the largest
    # link is shorter than the sum of the other three.
    #
    # If this condition is violated, the links cannot
    # form a closed chain.
    #
    # This check prevents impossible mechanisms from
    # being simulated.
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
    #
    # Some four-bar linkages have special geometric
    # symmetry that produces characteristic motion.
    #
    # These are detected before performing the general
    # Grashof classification.
    # ----------------------------------

    special = None

    # Parallelogram linkage
    #
    # Opposite links are equal:
    # L1 = L3 and L2 = L4
    #
    # This mechanism keeps opposite links parallel.
    if abs(L1 - L3) < tol and abs(L2 - L4) < tol:
        special = "Parallelogram"

    # Kite linkage
    #
    # Adjacent links are equal in pairs.
    # Often used in symmetrical motion designs.
    elif abs(L1 - L2) < tol and abs(L3 - L4) < tol:
        special = "Kite Linkage"

    # Rhomboid (Galloway) linkage
    #
    # Another symmetric configuration where
    # opposite adjacent links match.
    elif abs(L1 - L4) < tol and abs(L2 - L3) < tol:
        special = "Rhomboid (Galloway)"

    # ----------------------------------
    # 3️⃣ Grashof Classification
    # ----------------------------------
    #
    # The Grashof condition determines whether at least
    # one link in the four-bar linkage can rotate fully.
    #
    # Let:
    #   s = shortest link
    #   l = longest link
    #   p, q = remaining links
    #
    # Grashof condition:
    #
    #   s + l ≤ p + q
    #
    # Classification:
    #
    #   s + l < p + q → Grashof
    #   s + l = p + q → Change-Point
    #   s + l > p + q → Non-Grashof
    #
    # Change-point mechanisms pass through a singular
    # configuration where the linkage becomes collinear.
    # ----------------------------------

    s = min(links)
    l = max(links)

    # Extract the remaining two links
    temp = links.copy()
    temp.remove(s)
    temp.remove(l)
    p, q = temp

    # Grashof index
    GI = (p + q) - (s + l)

    if GI > tol:
        grashof_class = "Grashof"
    elif GI < -tol:
        grashof_class = "Non-Grashof"
    else:
        grashof_class = "Change-Point"

    # ----------------------------------
    # 4️⃣ Mechanism Type Classification
    # ----------------------------------
    #
    # The mechanism type depends on which link is
    # the shortest link and whether the linkage is
    # Grashof or Non-Grashof.
    #
    # Common mechanism types:
    #
    # Double Crank
    #     Both input and output links rotate fully.
    #
    # Crank-Rocker
    #     Input rotates fully, output oscillates.
    #
    # Rocker-Crank
    #     Input oscillates, output rotates fully.
    #
    # Double Rocker
    #     Both input and output oscillate.
    # ----------------------------------

    mechanism = "-"
    input_type = "-"
    output_type = "-"

    # ----------------------------------
    # Special symmetric linkages
    # ----------------------------------
    #
    # These are treated separately since their motion
    # characteristics are known from geometry alone.
    # ----------------------------------

    if special:
        mechanism = special
        input_type = "Crank"
        output_type = "Crank"

    # ----------------------------------
    # Non-Grashof mechanism
    #
    # No link can rotate fully.
    # All links act as rockers.
    # ----------------------------------

    elif grashof_class == "Non-Grashof":
        mechanism = "Double Rocker"
        input_type = "Rocker"
        output_type = "Rocker"

    # ----------------------------------
    # Grashof mechanisms
    #
    # Determine which link is shortest to identify
    # the motion configuration.
    # ----------------------------------

    else:

        # Shortest link is ground
        # → Double crank mechanism
        if abs(L1 - s) < tol:
            mechanism = "Double Crank"
            input_type = "Crank"
            output_type = "Crank"

        # Shortest link is input
        # → Crank-rocker
        elif abs(L2 - s) < tol:
            mechanism = "Crank-Rocker"
            input_type = "Crank"
            output_type = "Rocker"

        # Shortest link is output
        # → Rocker-crank
        elif abs(L4 - s) < tol:
            mechanism = "Rocker-Crank"
            input_type = "Rocker"
            output_type = "Crank"

        # Shortest link is coupler
        # → Double rocker
        else:
            mechanism = "Double Rocker"
            input_type = "Rocker"
            output_type = "Rocker"

        # Add label if this is a change-point mechanism
        if grashof_class == "Change-Point":
            mechanism += " (Change-Point)"

    # ----------------------------------
    # Return classification results
    # ----------------------------------

    return {
        "Assembly": "Valid",
        "Grashof Class": grashof_class,
        "Mechanism Type": mechanism,
        "Input Type": input_type,
        "Output Type": output_type
    }