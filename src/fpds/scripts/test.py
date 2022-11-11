import requests
from xml.etree import ElementTree
from fpds.core.parser import fpdsXML, _ElementAttributes


URL = 'https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC&q=LAST_MOD_DATE:[2021/05/02,2022/05/03] AGENCY_CODE:"7504"'
resp = requests.get(URL)

xml = fpdsXML(resp.content)
ns = xml.namespace_dict
entries = xml.tree.findall('.//ns0:entry', ns)

entry = entries[0]
elem = entry.find('.//ns1:contractActionType', ns)
attrib = elem.attrib






