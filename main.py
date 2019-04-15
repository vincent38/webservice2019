# -encoding:utf-8
from template.appengine import *
from template.unit import *
OAUTH_TOKEN="xoxp-342204927924-342571726693-607813590900-d585b09efdecbf3646852194ced0a802"
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
			if "user" in c:
				unit(area="message",smalljson=c).put()
				http.post("https://slack.com/api/chat.postMessage", {
					'token': OAUTH_TOKEN,
					'channel': c['channel'],
					'text': c["text"],
					'username': 'shrike',
					'icon_url': urlformat(request,"{host}/icon.png"),
				})
			else:
				pass
def hello(request):
	n=unit.query(unit.area=="message").order(-unit.born).fetch()
	return jsonres([i.smalljson for i in n])
def push(request):
	c=unit.query(unit.area=="message").order(-unit.born).get().smalljson
	http.post("https://slack.com/api/chat.postMessage", {
		'token': OAUTH_TOKEN,
		'channel': c['channel'],
		'text': c["text"],
		'username': c["text"]
	})

app = wsgiapp([(r"/products/(\d+)",testfunc), ('/slack', helloslack), ('/push', push), ('/', hello)])
# http://localhost:8080/products/1, Your requested Product %1,