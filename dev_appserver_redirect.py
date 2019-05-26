# -*- coding: utf-8 -*-
import os,sys
for v in os.environ.get("PATH").split(";"):
	if v.find("google-cloud-sdk")>0 and v.find("bin"):
		sys.path.append(v)
		execfile(os.path.join(v,"dev_appserver.py"))
		break