# -encoding:utf-8
from template.appengine import *
OAUTH_TOKEN="xoxp-342204927924-342571726693-597198151425-110aed279f204310b53881202363066b"
def testfunc(request, *args, **kwargs):
	r=http.get("http://info.cern.ch/hypertext/WWW/TheProject.html")
	return textres('You requested product<br>{0}<br>{1}'.format(json.dumps(args),json.dumps(kwargs)))
def helloslack(request,*args,**kwargs):
	a=getjson(request)
	b=a["type"]
	if b=="url_verification":
		return textres(a["challenge"])
	if b=="event_callback":
		c=a["event"]
		d=c["type"]
		if d=="message":
			http.post("https://slack.com/api/chat.postMessage",{
				'token': OAUTH_TOKEN,
				'channel': c['channel'],
				'text': c["text"],
				'username': c["text"]
			})

app = wsgiapp([(r"/products/(\d+)",testfunc), ('/slack', helloslack)])
# http://localhost:8080/products/1, Your requested Product %1,