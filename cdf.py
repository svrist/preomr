# From "Reject Options and Confidence Measures for kNN Classifiers"
# By Christoph Dalitz
# Hochschule Niederrhein
# Fachbereich Elektrotechnik und Informatik
# Reinarzstr. 49, 47805 Krefeld, Germany
# 17. June 2009
#

class EmpiricalCDF(object):
    def __init__(self, data):
        self.n = len(data)
        self.data = [x for x in data] # copy data
        self.data.sort()

    def cdf(self, x):
        from bisect import bisect
        pos = bisect(self.data, x)
        if pos < 1:
            return 0.0
        elif pos >= self.n:
            return 1.0
        else:
            # linear interpolation between neighboring points
            a = self.data[pos-1];
            b = self.data[pos]
            return float(pos + float(x - a)/(b-a)) / self.n

    def invcdf(self, q):
        pos = int(q*self.n)
        if pos >= self.n:
            return self.data[self.n-1]
        elif pos <= 0:
            return self.data[0]
        else:
            # linear interpolation between neighboring points
            a = self.data[pos-1]
            b = self.data[pos]
            fa = float(pos)/self.n
            fb = float(pos+1)/self.n
            return (q-fa)*(b-a)/(fb-fa) + a
