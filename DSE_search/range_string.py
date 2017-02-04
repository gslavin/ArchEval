


class RangeString:
    """
    Encapsulates the parsing, error checking, and range checking for strings
    which represent hard range constraints.
    """

    def __init__(self, s):
        if (s[0] != '(' and s[0] != '['):
            raise ValueError("Range string does not match acceptable pattern.")
        
        if (s[-1] != ')' and s[-1] != ']'):
            raise ValueError("Range string does not match acceptable pattern.")

        s_new = s.replace('(', '')
        s_new = s_new.replace('[', '')
        s_new = s_new.replace(')', '')
        s_new = s_new.replace(']', '')
        s_new = s_new.replace(',', ' ')

        (l, r) = [t(s) for t, s in zip((float, float), s_new.split())]

        if (l > r):
            raise ValueError("Larger number incorrectly specified first.")

        if (l == r and (s[0] == '(' or s[-1] == ')')):
            raise ValueError("Same values specified, but at least one end marker \
            is non-inclusive.")
        
        self.low = l
        self.high = r
        self.lower_inclusive = s[0] == '['
        self.upper_inclusive = s[-1] == ']'

    def in_range(self, f):
        """
        Determines whether float f is within the range specified by this range
        string.
        """
        
        if ((self.lower_inclusive and f < self.low) or
            (not self.lower_inclusive and f <= self.low)):
            return False

        if ((self.upper_inclusive and f > self.high) or
            (not self.upper_inclusive and f >= self.high)):
            return False
        
        return True
