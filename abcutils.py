
def extractMultiname(abc, mni):
	pool = abc.constant_pool
	mn = pool.multiname[mni]
	data = mn.data
	name = pool.string[data.name].utf8
	nsi = data.ns
	return name, nsi

def extractNamespace(abc, nsi):
	pool = abc.constant_pool
	ns = pool.namespace[nsi]
	name = pool.string[ns.name].utf8
	visibility = None
	if ns.kind in (0x8, 0x16, 0x17):
		visibility = 'public'
	elif ns.kind == 0x18:
		visibility = 'protected'
	elif ns.kind == 0x05:
		visibility = 'private'
	return name, visibility
