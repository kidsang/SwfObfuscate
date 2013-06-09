
class ABCTracer():

	def __init__(self, abcFile):
		self.abc = abcFile

	def Read(self):
		abc = self.abc
		out = ''
		out += ReadHeader(abc)
		out += ReadConstPool(abc)
		out += ReadMethodInfo(abc)
		out += ReadMetadataInfo(abc)
		out += ReadInstanceInfo(abc)
		out += ReadClassInfo(abc)
		out += ReadScriptInfo(abc)
		out += ReadMethodBodyInfo(abc)
		return out

def FormatLineNo(cur):
	base = 16
	row = cur / base
	col = cur % base
	return 'row:%x, col:%x' %(row, col)

def ReadHeader(abc):
	out = '\n'
	out += 'tag_code: ' + str(abc.tagCode) + '\n'
	out += 'flags: ' + str(abc.flags) + '\n'
	out += 'file_name: ' + str(abc.name) + '\n'
	out += 'major_version: ' + str(abc.major_version) + '\n'
	out += 'minor_version: ' + str(abc.minor_version) + '\n'
	return out

def ReadConstPool(abc):
	pool = abc.constant_pool
	out = '\n'
	out += 'constant_pool\n'
	pre = 4 * ' '

	out += pre + 'int_count: ' + str(pool.int_count) + '\n'
	out += pre + 'integer: ' + str(pool.integer) + '\n'

	out += pre + 'uint_count: ' + str(pool.uint_count) + '\n'
	out += pre + 'uinteger: ' + str(pool.uinteger) + '\n'

	out += pre + 'double_count: ' + str(pool.double_count) + '\n'
	out += pre + 'double: ' + str(pool.double) + '\n'

	out += pre + 'string_count: ' + str(pool.string_count) + '\n'
	out += pre + 'string:\n'
	out += pre + '[\n'
	pre = 8 * ' '
	strings = [''] * pool.string_count
	for i in range(1, pool.string_count):
		string = pool.string[i].utf8
		strings[i] = string
		out += pre + str(i) + ': ' + string + '\n'
	pre = 4 * ' '
	out += pre + ']\n'

	out += pre + 'namespace_count: ' + str(pool.namespace_count) + '\n'
	out += pre + 'namespace:\n'
	out += pre + '[\n'
	pre = 8 * ' '
	nss = [''] * pool.namespace_count
	for i in range(1, pool.namespace_count):
		ns = pool.namespace[i]
		nss[i] = strings[ns.name]
		out += pre + str(i) + ': <kind:' + ns.kind_map[ns.kind] 
		out += ', name:' + strings[ns.name] 
		out += ', name: ' + str(ns.name) + '>\n'
	pre = 4 * ' '
	out += pre + ']\n'

	out += pre + 'ns_set_count: ' + str(pool.ns_set_count) + '\n'
	out += pre + 'ns_set:\n'
	out += pre + '[\n'
	pre = 8 * ' '
	nssets = [''] * pool.ns_set_count
	for i in range(1, pool.ns_set_count):
		nsset = pool.ns_set[i]
		nssets[i] = '['
		for j in range (nsset.count):
			nssets[i] += nss[nsset.ns[j]] + ', ' 
		nssets[i] += ']'
		out += pre + str(i) + ': <count:' + str(nsset.count)
		out += ', ns:' + nssets[i]
		out += ', ns:' + str(nsset.ns) + '>\n'
	pre = 4 * ' '
	out += pre + ']\n'

	out += pre + 'multiname_count: ' + str(pool.multiname_count) + '\n'
	out += pre + 'multiname:\n'
	out += pre + '[\n'
	pre = 8 * ' '
	for i in range(1, pool.multiname_count):
		mn = pool.multiname[i]
		mndata = mn.data
		out += pre + str(i) + ': <kind:' + mn.kind_map[mn.kind]
		if mn.kind in (0x07, 0x0D):
			out += ', ns:' + nss[mndata.ns]
			out += ', ns:' + str(mndata.ns)
			out += ', name:' + strings[mndata.name]
			out += ', name:' + str(mndata.name)
		elif mn.kind in (0x0F, 0x10):
			out += ', name:' + strings[mndata.name]
			out += ', name:' + str(mndata.name)
		elif mn.kind in (0x11, 0x12):
			out += ''
		elif mn.kind in (0x09, 0x0E):
			out += ', name:' + strings[mndata.name]
			out += ', name:' + str(mndata.name)
			out += ', ns_set:' + nssets[mndata.ns_set]
			out += ', ns_set:' + str(mndata.ns_set)
		elif mn.kind in (0x1B, 0x1C):
			out += ', ns_set:' + nssets[mndata.ns_set]
			out += ', ns_set:' + str(mndata.ns_set)
		out += '>\n'

	pre = 4 * ' '
	out += pre + ']\n'

	return out

def GetInt(abc, i):
	val = abc.constant_pool.integer[i]
	return str(val)

def GetUInt(abc, i):
	val = abc.constant_pool.uinteger[i]
	return str(val)

def GetDouble(abc, i):
	val = abc.constant_pool.double[i]
	return str(val)

def GetString(abc, i):
	s = abc.constant_pool.string[i]
	if i == 0:
		return str(s)
	return s.utf8

def GetNamespace(abc, i):
	ns = abc.constant_pool.namespace[i]
	if i == 0:
		return str(ns)

	out = '<kind:' + ns.kind_map[ns.kind] 
	out += ', name:' + GetString(abc, ns.name) + '>'
	return out

def GetNsSet(abc, i):
	nsset = abc.constant_pool.ns_set[i]
	if i == 0:
		return str(nsset)

	out = '['
	for i in range (nsset.count):
		out += GetNamespace(abc, nsset.ns[i]) + ', ' 
	out += ']'
	return out

def GetMultiname(abc, i):
	mn = abc.constant_pool.multiname[i]
	if i == 0:
		return str(mn)

	mndata = mn.data
	out = '<' 
	if mn.kind in (0x07, 0x0D):
		out += 'name:' + GetString(abc, mndata.name)
		out += ', ns:' + GetNamespace(abc, mndata.ns)
	elif mn.kind in (0x0F, 0x10):
		out += 'name:' + GetString(abc, mndata.name)
	elif mn.kind in (0x11, 0x12):
		out += ''
	elif mn.kind in (0x09, 0x0E):
		out += 'name:' + GetString(abc, mndata.name)
		out += ', ns_set:' + GetNsSet(abc, mndata.ns_set)
	elif mn.kind in (0x1B, 0x1C):
		out += 'ns_set:' + GetNsSet(abc, mndata.ns_set)
	out += ', kind:' + mn.kind_map[mn.kind] + '>'
	return out

def GetValByType(abc, i, t):
	if t == 0x03:
		return GetInt(abc, i)
	elif t == 0x04:
		return GetUInt(abc, i)
	elif t == 0x06:
		return GetDouble(abc, i)
	elif t == 0x01:
		return GetString(abc, i)
	elif t in (0x08, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x05):
		return GetNamespace(abc, i)
	else:
		return ''

def ReadMethodInfo(abc):
	methods = abc.method

	out = '\n'
	out += 'method_count: ' + str(abc.method_count) + '\n'

	out += 'method:\n'
	out += '[\n'
	for i in range(abc.method_count):
		method = methods[i]
		pre = 4 * ' '
		out += pre + str(i) + ':' + 'method\n'
		pre = 8 * ' '
		out += pre + 'name: ' + GetString(abc, method.name) + '\n'
		out += pre + 'param_count: ' + str(method.param_count) + '\n'
		out += pre + 'return_type: ' + GetMultiname(abc, method.return_type) + '\n'
		out += pre + 'param_type:\n'
		out += pre + '[\n'
		pre = 12 * ' '
		for j in range(method.param_count):
			out += pre + GetMultiname(abc, method.param_type[j]) + '\n'
		pre = 8 * ' '
		out += pre + ']\n'
		out += pre + 'flags: ' + str(method.flags) + '\n'
		if method.flags & 0x08:
			options = method.options
			out += pre + 'options:\n'
			out += pre + '[\n'
			pre = 12 * ' '
			for j in range(options.option_count):
				option = options.option[j]
				out += pre + 'val:' + GetValByType(abc, option.val, option.kind) + ', '
				out += 'kind:' + option.kind_map[option.kind] + '\n'
			pre = 8 * ' '
			out += pre + ']\n'
		if method.flags & 0x80:
			out += pre + 'param_names:['
			for j in range(method.param_count):
				out += GetString(abc, method.param_names[j]) + ', '
			out += ']\n'
		out += '\n'
	out += ']\n'

	return out

def ReadMetadataInfo(abc):
	metas = abc.metadata

	out = '\n'
	out += 'metadata_count: ' + str(abc.metadata_count) + '\n'

	out += 'metadata:\n'
	out += '[\n'
	for i in range(abc.metadata_count):
		meta = metas[i]
		pre = 4 * ' '
		out += pre + str(i) + ':' + GetString(abc, meta.name) + '\n'
		pre = 8 * ' '
		out += pre + 'item_count: ' + str(meta.item_count) + '\n'
		out += pre + 'item_info:\n'
		out += pre + '[\n'
		pre = 12 * ' '
		for j in range(meta.item_count):
			item = meta.items[j]
			out += pre + 'key:' + GetString(abc, item.key) + ', '
			out += 'value:' + GetString(abc, item.value) + '\n'
		pre = 8 * ' '
		out += pre + ']\n'
	out += ']\n'

	return out

def ReadTraits(abc, trait_count, traits, indent):
	out = ''
	pre = indent * ' '
	out += pre + 'trait_count: ' + str(trait_count) + '\n'
	out += pre + 'trait:\n'
	out += pre + '[\n'
	for j in range(trait_count):
		pre = (indent + 4) * ' '
		trait = traits[j]
		out += pre + 'name:' + GetMultiname(abc, trait.name) + '\n'
		out += pre + 'kind:' + trait.kind_map[trait.kind_kind] + '\n'

		out += pre + 'data:' + '\n'
		pre = (indent + 8) * ' '
		data = trait.data
		if trait.kind_kind in (0, 6):
			out += pre + 'slot_id:' + str(data.slot_id) + '\n'
			out += pre + 'type_name:' + GetMultiname(abc, data.type_name) + '\n'
			if data.vindex != 0:
				out += pre + 'value:' + GetValByType(abc, data.vindex, data.vkind) + '\n'
		elif trait.kind_kind in (4,):
			out += pre + 'slot_id:' + str(data.slot_id) + '\n'
			out += pre + 'classi:' + str(data.classi) + '\n'
		elif trait.kind_kind in (5,):
			out += pre + 'slot_id:' + str(data.slot_id) + '\n'
			out += pre + 'function:' + str(data.function) + '\n'
		elif trait.kind_kind in (1, 2, 3):
			out += pre + 'disp_id:' + str(data.disp_id) + '\n'
			out += pre + 'method:' + str(data.method) + '\n'
		pre = (indent + 4) * ' '

		if trait.kind_attr & 0x04:
			out += pre + 'metadata_count:' + str(trait.metadata_count) + '\n'
			out += pre + 'metadata:['
			for k in range(trait.metadata_count):
				out += str(trait.metadata[k]) + ', '
			out +=  ']\n'
	pre = indent * ' '
	out += pre + ']\n'
	return out


def ReadInstanceInfo(abc):
	insts = abc.instance

	out = '\n'
	out += 'instance_count: ' + str(abc.class_count) + '\n'

	out += 'instance:\n'
	out += '[\n'
	for i in range(abc.class_count):
		inst = insts[i]
		pre = 4 * ' '
		out += pre + str(i) + ':' + GetMultiname(abc, inst.name) + '\n'
		pre = 8 * ' '
		out += pre + 'super_name: ' + GetMultiname(abc, inst.super_name) + '\n'
		out += pre + 'flags: ' + str(inst.flags) + '\n'
		if inst.flags & 0x08:
			out += pre + 'protectedNs: ' + GetNamespace(abc, inst.protectedNs) + '\n'

		out += pre + 'intrf_count: ' + str(inst.intrf_count) + '\n'
		out += pre + 'interface:\n'
		out += pre + '[\n'
		pre = 12 * ' '
		for j in range(inst.intrf_count):
			out += pre + GetMultiname(abc, inst.interface[j]) + '\n'
		pre = 8 * ' '
		out += pre + ']\n'

		out += pre + 'iinit: ' + str(inst.iinit) + '\n'

		out += ReadTraits(abc, inst.trait_count, inst.trait, 8)

	out += ']\n'

	return out

def ReadClassInfo(abc):
	clss = abc.cls

	out = '\n'
	out += 'class_count: ' + str(abc.class_count) + '\n'

	out += 'class:\n'
	out += '[\n'
	for i in range(abc.class_count):
		cls = clss[i]
		pre = 4 * ' '
		out += pre + str(i) + ':class\n'
		pre = 8 * ' '
		out += pre + 'cinit: ' + str(cls.cinit) + '\n'
		out += ReadTraits(abc, cls.trait_count, cls.trait, 8)

	out += ']\n'

	return out

def ReadScriptInfo(abc):
	scripts = abc.script

	out = '\n'
	out += 'script_count: ' + str(abc.script_count) + '\n'

	out += 'script:\n'
	out += '[\n'
	for i in range(abc.script_count):
		script = scripts[i]
		pre = 4 * ' '
		out += pre + str(i) + ':script\n'
		pre = 8 * ' '
		out += pre + 'init: ' + str(script.init) + '\n'
		out += ReadTraits(abc, script.trait_count, script.trait, 8)

	out += ']\n'

	return out

def ReadMethodBodyInfo(abc):
	bodies = abc.method_body
	out = '\n'
	out += 'method_body_count: ' + str(abc.method_body_count) + '\n'

	out += 'method_body:\n'
	out += '[\n'
	for i in range(abc.method_body_count):
		body = bodies[i]
		pre = 4 * ' '
		out += pre + str(i) + ':method_body\n'
		pre = 8 * ' '
		out += pre + 'method: ' + str(body.method) + '\n'
		out += pre + 'max_stack: ' + str(body.max_stack) + '\n'
		out += pre + 'local_count: ' + str(body.local_count) + '\n'
		out += pre + 'init_scope_depth: ' + str(body.init_scope_depth) + '\n'
		out += pre + 'max_scope_depth: ' + str(body.max_scope_depth) + '\n'
		out += pre + 'code_length: ' + str(body.code_length) + '\n'
		out += pre + 'exception_count: ' + str(body.exception_count) + '\n'

		out += ReadTraits(abc, body.trait_count, body.trait, 8)
		out += '\n'

	out += ']\n'

	return out
