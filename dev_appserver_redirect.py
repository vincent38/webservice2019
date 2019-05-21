# -*- coding: utf-8 -*-
import sys,os
for v in os.environ.get("PATH").split(";"):
	if v.find("google-cloud-sdk")>0:
		execfile("{0}/dev_appserver.py".format(v))
		break