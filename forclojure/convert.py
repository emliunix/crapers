# coding: utf-8

import json

with open("restrictions.json", "r") as i:
	with open("output.csv", "w") as o:
		objs = json.load(i)
		for obj in objs:
			l = []
			for v in obj.values():
			 	if isinstance(v, list):
				 	l.append("\"{%s}\"" % (",".join(v)))
				else:
					l.append(str(v))
			o.write(",".join(l))
			o.write("\n")

