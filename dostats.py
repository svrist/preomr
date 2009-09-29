
class Ir_classification:

    def __init__(self,found,fp,fn):
        self._found = found
        self._fp = fp
        self._fn = fn
        self._tp = found-fp
        self._real = self._tp + self._fn

    def precision(self):
        return self._tp/float(self._found)

    def recall(self):
        return self._tp/float(self._real)

    def fn_rate(self):
        return self._fn/float(self._real)

    def fp_rate(self):
        return self._fp/float(self._real)

    def f_measure(self,beta=0.5):
        return (1+beta**2.0)*\
                ((self.precision() * self.recall() ) /
                 (beta**2.0 * self.precision() + self.recall())
                )


if __name__ == '__main__':
    import yaml
    import sys
    text = {"found":0, "falsepositive":0,"falsenegative":0}
    dynamic = {"found":0, "falsepositive":0,"falsenegative":0}
    for f in sys.argv[1:]:
        if f[-4:] == "yaml":
            fil = open(f)
            data = yaml.load(fil)
            for key,value in text.iteritems():
                if key in data["text"]:
                    text[key] += data["text"][key]
                if key in data["dynamics"]:
                    dynamic[key] += data["dynamics"][key]
        else:
            print "%s has questionable filetype?(%s)"%(f,f[-4:])

    print "Text: %s"%text

    textc = Ir_classification(text["found"], text["falsepositive"],
                                  text["falsenegative"])
    dync = Ir_classification(dynamic["found"], dynamic["falsepositive"],
                               dynamic["falsenegative"])


    print "\tFN Rate: %.4f"%textc.fn_rate()
    print "\tFP Rate: %.4f"%textc.fp_rate()
    print "\tPrecision: %.4f"%textc.precision()
    print "\tRecall: %.4f"%textc.recall()
    print "\tF_0.5: %.4f"%textc.f_measure()
    # print "\tFN rate: %.2f%%"%(text["falsenegative"]/float(text["found"]+text["falsenegative"]-text["falsepositive"])*100)
    #print "\tFP rate: %.2f%%"%(text["falsepositive"]/float(text["found"]+text["falsenegative"]-text["falsepositive"])*100)
    print 

    print "Dynamics: %s"%dynamic
    #print "\tFN rate: %.2f%%"%(dynamic["falsenegative"]/float(dynamic["found"]+dynamic["falsenegative"]-dynamic["falsepositive"])*100)
    #print "\tFP rate: %.2f%%"%(dynamic["falsepositive"]/float(dynamic["found"]+dynamic["falsenegative"]-dynamic["falsepositive"])*100)
    print "\tFN Rate: %.4f"%dync.fn_rate()
    print "\tFP Rate: %.4f"%dync.fp_rate()
    print "\tPrecision: %.4f"%dync.precision()
    print "\tRecall: %.4f"%dync.recall()
    print "\tF_0.5: %.4f"%dync.f_measure()
