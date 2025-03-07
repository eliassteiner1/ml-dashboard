import numpy as np
import matplotlib.colors as mcolors
import bisect

  
def adjust_alpha(color: str, adjust_a: float):
    """Takes a css "color name", "rgb(r, g, b)", or "rgba(r, g, b, a)" string and outputs the color in "rgba" format
    with adjust_a times the original alpha value."""
    
    if color.startswith("rgb"):
        components = color[color.index("(")+1:color.index(")")].split(",")
        r, g, b    = map(int, components[:3])  # Extract RGB components
        a          = float(components[3]) if len(components) == 4 else 1.0  # a assumed to be 1.0 if not provided
    else:
        # Assume it's a CSS color name
        r, g, b = [int(c * 255) for c in mcolors.to_rgb(color)]
        a = 1.0

    a *= adjust_a
    a = max(0, min(a, 1)) # Ensure alpha stays in range [0, 1]
    return f"rgba({r}, {g}, {b}, {a:.3f})"

def determine_single_range(MIN: float, MAX: float, factor: float):
    """ MAX is max over all tracex and MIN is min over all traces """
    
    if MAX < MIN:
        raise ValueError(f"MAX should not be smaller than MIN! (got {MAX=}, {MIN=})")
    
    possible = [(1+factor)*MAX, -factor*MAX, (1+factor)*MIN, -factor*MIN]
    rng      = [min(possible), max(possible)]
    return rng

def determine_mixed_range(RNG1: list, RNG2: list):
    """ determines the best range for a subplot mixed y axis range so that both ranges have the same ratio of above zeroline and below zeroline spans. assumes max is > 0 and min is < 0!"""

    # use a geometric mean of both ratios to find a sensible ratio that works the best for both
    R1_ORIG = RNG1[1] / -RNG1[0] 
    R2_ORIG = RNG2[1] / -RNG2[0]
    RBAR    = (R1_ORIG * R2_ORIG)**0.5
    
    # then, scale both old ratios, so that they obey the geometric mean ratio. but scale the ratios, so that ranges are only axpanded and not shortened, in order not to clip any data 
    
    # new primary range
    if R1_ORIG > RBAR:
        RNG1[0] = (R1_ORIG / RBAR) * RNG1[0]
        RNG1[1] = RNG1[1]
    if R1_ORIG < RBAR:
        RNG1[0] = RNG1[0]
        RNG1[1] = (RBAR / R1_ORIG) * RNG1[1]
        
    # new secondary range
    if R2_ORIG > RBAR:
        RNG2[0] = (R2_ORIG / RBAR) * RNG2[0]
        RNG2[1] = RNG2[1]
    if R2_ORIG < RBAR:
        RNG2[0] = RNG2[0]
        RNG2[1] = (RBAR / R2_ORIG) * RNG2[1]
        
    return RNG1, RNG2

def idx_next_smaller(seq: list | np.ndarray, new_element: float):
    """ returns the index of the element in the list that is the next smallest to new_element. when new_element would be exactly the same as one in the sequence, the position is tiebroken to be on the right side of the equal one. """

    if isinstance(seq, list):
        idx = bisect.bisect_left(seq, new_element)
        return idx if new_element == seq[idx] else np.clip(idx-1, a_min=0, a_max=None)
        
    if isinstance(seq, np.ndarray):
        idx = np.searchsorted(seq, new_element)
        return idx if new_element == seq[idx] else np.clip(idx-1, a_min=0, a_max=None)

    raise TypeError(f"the sequence input has to be either a list or and np.ndarray!") 
