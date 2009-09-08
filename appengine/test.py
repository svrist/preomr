import urllib

from django.utils import simplejson as json
def add_work(id):
    url = "http://localhost:8080/add?%s"
    fetch_url = 'http://www.free-scores.com/PDF/anschutz-ernst-mon-beau-sapin-14315.pdf'
    jd = {
            'url':fetch_url,
            'author': id,
            'type':'pdf'
        }
    qs = urllib.urlencode(jd)
    result = urllib.urlopen(url%qs)

    data = json.loads(result.read())
    print "Status: %s: %s"%(data['status'],data['msg'])

def add_author():
    url = "http://localhost:8080/author/create?%s"
    qs= {
            'name':'The Author!',
        }
    qs = urllib.urlencode(qs)
    result = urllib.urlopen(url%qs)
    data = json.loads(result.read())
    print "Status: %s: %s"%(data['status'],data['msg'])

    return data['id']


if __name__ == "__main__":
    a = add_author()
    add_work(a)
    
