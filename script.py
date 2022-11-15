from src.fpds.core.parser import fpdsRequest, fpdsXML, _ElementAttributes
params_dict = {'LAST_MOD_DATE': '[2022/01/01, 2022/05/01]', 'AGENCY_CODE': '"7504"'}
f = fpdsRequest(**params_dict)
f.create_content_iterable()
xml = fpdsXML(f.content[0])
entries = xml.get_atom_feed_entries()
entry = entries[0]
for i in xml.parse_items(entry):
    elem = _ElementAttributes(i, xml.namespace_dict)
    print(elem._generate_nested_attribute_dict())