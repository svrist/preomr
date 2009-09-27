
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
    print "\tFN rate: %.2f%%"%(text["falsenegative"]/float(text["found"]+text["falsenegative"])*100)
    print "\tFP rate: %.2f%%"%(text["falsepositive"]/float(text["found"]+text["falsenegative"]-text["falsepositive"])*100)
    print 
    print "Dynamics: %s"%dynamic
    print "\tFN rate: %.2f%%"%(dynamic["falsenegative"]/float(dynamic["found"]+dynamic["falsenegative"])*100)
    print "\tFP rate: %.2f%%"%(dynamic["falsepositive"]/float(dynamic["found"]+dynamic["falsenegative"]-dynamic["falsepositive"])*100)

