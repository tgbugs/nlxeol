import urllib
import re

cat=urllib.urlopen("http://neurolex.org/wiki/Category:%s").read()
re.findall("'\*ids", )