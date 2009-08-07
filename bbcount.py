
def ccs_counter(ccs):

    ret = {}
    for c in ccs:
        key ="%dx%d"%(c.ncols,c.nrows)
        if not ret.has_key(key):
            ret[key] = []

        ret[key].append(c)

    return ret


