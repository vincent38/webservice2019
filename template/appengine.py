import webapp2,json,http,os
from google.appengine.ext.webapp import template, blobstore_handlers, RequestHandler
from google.appengine.api import urlfetch, app_identity, mail, memcache

if True:
    def httpfunc(method,url,header,data):
        method={"POST":urlfetch.POST,"GET":urlfetch.GET}[method]
        r=urlfetch.fetch(url=url, payload=data, method=method, headers=header)
        return (r.status_code, r.content)
    http.httpfunc = httpfunc
def wsgiapp(accesstable):
    return webapp2.WSGIApplication(accesstable)
def textres(content,**kwargs):
    headers={}
    if "type" in kwargs:
        headers['Content-Type'] = kwargs["type"]
    return webapp2.Response(content,headers=headers)
def tempres(temp,params,**kwargs):
    tmp = os.path.join(os.path.dirname(__file__), "../" + temp)
    return textres(template.render(tmp, params),**kwargs)
def jsonres(content):
    return webapp2.Response(json.dumps(content))
def getjson(request):
    return json.loads(request.body)
def urlformat(request,formatstring,**kwargs):
    return formatstring.format(host=request.host_url,path=request.path,query=request.query_string,**kwargs)

class BlobHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        self.send_blob(photo_key)