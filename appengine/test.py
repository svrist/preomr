import urllib

from django.utils import simplejson as json

if __name__ == "__main__":
    url = "http://localhost:8080/add"
    fetch_url = 'http://www.free-scores.com/PDF/anschutz-ernst-mon-beau-sapin-14315.pdf'
    jd = json.dumps(
        {
            'mydata':'test',
            'url':fetch_url,
            'type':'pdf'
        }
    )
    form_fields = {
        'data' : jd
    }
    form_data = urllib.urlencode(form_fields)
    result = urllib.urlopen(url,data=form_data)
    data = json.loads(result.read())

    print "Status: %s: %s"%(data['status'],data['msg'])
