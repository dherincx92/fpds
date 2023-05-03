from fpds import fpdsRequest
from fpds.core._xml import Entry, fpdsXML

request = fpdsRequest(LAST_MOD_DATE="[2013/10/29, 2013/10/30]", AGENCY_CODE="4740")
request.send_request()
tree = request.content[0]

xml = fpdsXML(tree)
entries = xml.get_atom_feed_entries()
entry = entries[0]

e = Entry(entry)
