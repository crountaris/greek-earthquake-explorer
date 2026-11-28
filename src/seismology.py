import numpy as np

def b_value(magnitudes, mc, dm=0.1):
    """ Aki-Utsu maximum likelihood b-value for magnitudes at or above mc."""
    above = magnitudes[magnitudes >= mc]
    b = np.log10(np.e) / (above.mean() - (mc - dm/2))
    error = b /np.sqrt(len(above))
    return b, error, len(above)