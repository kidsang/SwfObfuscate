from prime import *

def FormatLineNo(cur):
	base = 16
	row = cur / base
	col = cur % base
	return 'row:%x, col:%x' %(row, col)

class ABCFile():

	def unpack(self, data, cur):

		cur, self.tagCode, length = ReadTagHeader(data, cur)
		cur, self.flags = ReadU32(data, cur)
		cur, self.name = ReadCString(data, cur)
		cur, self.minor_version = ReadU16(data, cur)
		cur, self.major_version = ReadU16(data, cur)

		self.constant_pool = cpool_info()
		cur = self.constant_pool.unpack(data, cur)

		cur, self.method_count = ReadU30(data, cur)
		self.method = []
		for i in range(self.method_count):
			method = method_info()
			cur = method.unpack(data, cur)
			self.method.append(method)

		cur, self.metadata_count = ReadU30(data, cur)
		self.metadata = []
		for i in range(self.metadata_count):
			metadata = metadata_info()
			cur = metadata.unpack(data, cur)
			self.metadata.append(metadata)

		cur, self.class_count = ReadU30(data, cur)
		self.instance = []
		for i in range(self.class_count):
			instance = instance_info()
			cur = instance.unpack(data, cur)
			self.instance.append(instance)
		self.cls = []
		for i in range(self.class_count):
			cls = class_info()
			cur = cls.unpack(data, cur)
			self.cls.append(cls)

		cur, self.script_count = ReadU30(data, cur)
		self.script = []
		for i in range(self.script_count):
			script = script_info()
			cur = script.unpack(data, cur)
			self.script.append(script)

		cur, self.method_body_count = ReadU30(data, cur)
		self.method_body = []
		for i in range(self.method_body_count):
			method_body = method_body_info()
			cur = method_body.unpack(data, cur)
			self.method_body.append(method_body)

		return cur

	def pack(self):
		data = ''
		data += WriteU32(self.flags)
		data += WriteCString(self.name)

		data += WriteU16(self.minor_version)
		data += WriteU16(self.major_version)

		data += self.constant_pool.pack()

		data += WriteU30(self.method_count)
		for i in range(self.method_count):
			data += self.method[i].pack()

		data += WriteU30(self.metadata_count)
		for i in range(self.metadata_count):
			data += self.metadata[i].pack()

		data += WriteU30(self.class_count)
		for i in range(self.class_count):
			data += self.instance[i].pack()
		for i in range(self.class_count):
			data += self.cls[i].pack()

		data += WriteU30(self.script_count)
		for i in range(self.script_count):
			data += self.script[i].pack()

		data += WriteU30(self.method_body_count)
		for i in range(self.method_body_count):
			data += self.method_body[i].pack()

		data = WriteTagHeader(self.tagCode, len(data)) + data

		return data

class cpool_info():

	def unpack(self, data, cur):

		cur, self.int_count = ReadU30(data, cur)
		self.integer = [0] * self.int_count
		for i in range(1, self.int_count):
			cur, val = ReadS32(data, cur)
			self.integer[i] = val

		cur, self.uint_count = ReadU30(data, cur)
		self.uinteger = [0] * self.uint_count
		for i in range(1, self.uint_count):
			cur, val = ReadU32(data, cur)
			self.uinteger[i] = val

		cur, self.double_count = ReadU30(data, cur)
		self.double = ['NaN'] * self.double_count
		for i in range(1, self.double_count):
			cur, val = ReadD64(data, cur)
			self.double[i] = val

		cur, self.string_count = ReadU30(data, cur)
		self.string = ['*'] * self.string_count
		for i in range(1, self.string_count):
			string = string_info()
			cur = string.unpack(data, cur)
			self.string[i] = string

		cur, self.namespace_count = ReadU30(data, cur)
		self.namespace = ['*'] * self.namespace_count
		for i in range(1, self.namespace_count):
			namespace = namespace_info()
			cur = namespace.unpack(data, cur)
			self.namespace[i] = namespace

		cur, self.ns_set_count = ReadU30(data, cur)
		self.ns_set = ['*'] * self.ns_set_count
		for i in range(1, self.ns_set_count):
			ns_set = ns_set_info()
			cur = ns_set.unpack(data, cur)
			self.ns_set[i] = ns_set

		cur, self.multiname_count = ReadU30(data, cur)
		self.multiname = ['*'] * self.multiname_count
		for i in range(1, self.multiname_count):
			multiname = multiname_info()
			cur = multiname.unpack(data, cur)
			self.multiname[i] = multiname

		return cur

	def pack(self):
		data = ''

		data += WriteU30(self.int_count)
		for i in range(1, self.int_count):
			data += WriteS32(self.integer[i])

		data += WriteU30(self.uint_count)
		for i in range(1, self.uint_count):
			data += WriteS32(self.uinteger[i])
		
		data += WriteU30(self.double_count)
		for i in range(1, self.double_count):
			data += WriteS32(self.double[i])
		
		data += WriteU30(self.string_count)
		for i in range(1, self.string_count):
			string = self.string[i]
			data += string.pack()

		data += WriteU30(self.namespace_count)
		for i in range(1, self.namespace_count):
			namespace = self.namespace[i]
			data += namespace.pack()
			
		data += WriteU30(self.ns_set_count)
		for i in range(1, self.ns_set_count):
			ns_set = self.ns_set[i]
			data += ns_set.pack()
		
		data += WriteU30(self.multiname_count)
		for i in range(1, self.multiname_count):
			multiname = self.multiname[i]
			data += multiname.pack()

		return data

class string_info():

	def unpack(self, data, cur):
		cur, self.size = ReadU30(data, cur)
		next = cur + self.size
		self.utf8 = data[cur:next]
		return next

	def pack(self):
		data = WriteU30(self.size)
		data += self.utf8
		return data

class namespace_info():

	kind_map = {
		0x08:'NameSpace',
		0x16:'PackageNamespace',
		0x17:'PackageInternalNs',
		0x18:'ProtectedNamespace',
		0x19:'ExplicitNamespace',
		0x1A:'StaticProtectedNs',
		0x05:'PrivateNs',
	}

	def unpack(self, data, cur):
		cur, self.kind = ReadU8(data, cur)
		cur, self.name = ReadU30(data, cur)
		return cur

	def pack(self):
		data = ''
		data += WriteU8(self.kind)
		data += WriteU30(self.name)
		return data

class ns_set_info():

	def unpack(self, data, cur):
		cur, self.count = ReadU30(data, cur)
		self.ns = []
		for i in range(self.count):
			cur, ns = ReadU30(data, cur)
			self.ns.append(ns)
		return cur

	def pack(self):
		data = ''
		data += WriteU30(self.count)
		for i in range(self.count):
			data += WriteU30(self.ns[i])
		return data

class multiname_info():

	kind_map = {
		0x07:'QName',
		0x0D:'QNameA',
		0x0F:'RTQName',
		0x10:'RTQNameA',
		0x11:'RTQNameL',
		0x12:'RTQNameLA',
		0x09:'Multiname',
		0x0E:'MultinameA',
		0x1B:'MultinameL',
		0x1C:'MultinameLA',
	}

	class QName():
		def unpack(self, data, cur):
			cur, self.ns = ReadU30(data, cur)
			cur, self.name = ReadU30(data, cur)
			return cur
		def pack(self):
			data = ''
			data += WriteU30(self.ns)
			data += WriteU30(self.name)
			return data

	class RTQName():
		def unpack(self, data, cur):
			cur, self.name = ReadU30(data, cur)
			return cur
		def pack(self):
			return WriteU30(self.name)

	class RTQNameL():
		def unpack(self, data, cur):
			return cur
		def pack(self):
			return ''

	class Multiname():
		def unpack(self, data, cur):
			cur, self.name = ReadU30(data, cur)
			cur, self.ns_set = ReadU30(data, cur)
			return cur
		def pack(self):
			data = ''
			data += WriteU30(self.name)
			data += WriteU30(self.ns_set)
			return data

	class MultinameL():
		def unpack(self, data, cur):
			cur, self.ns_set = ReadU30(data, cur)
			return cur
		def pack(self):
			return WriteU30(self.ns_set)

	def unpack(self, data, cur):
		cur, self.kind = ReadU8(data, cur)

		if self.kind in (0x07, 0x0D):
			self.data = self.QName()
		elif self.kind in (0x0F, 0x10):
			self.data = self.RTQName()
		elif self.kind in (0x11, 0x12):
			self.data = self.RTQNameL()
		elif self.kind in (0x09, 0x0E):
			self.data = self.Multiname()
		elif self.kind in (0x1B, 0x1C):
			self.data = self.MultinameL()

		cur = self.data.unpack(data, cur)
		return cur

	def pack(self):
		data = ''
		data += WriteU8(self.kind)
		data += self.data.pack()
		return data

class method_info():

	def unpack(self, data, cur):
		cur, self.param_count = ReadU30(data, cur)
		cur, self.return_type = ReadU30(data, cur)
		self.param_type = []
		for i in range(self.param_count):
			cur, t = ReadU30(data, cur)
			self.param_type.append(t)

		cur, self.name = ReadU30(data, cur)
		cur, self.flags = ReadU8(data, cur)

		if self.flags & 0x08:
			self.options = option_info()
			cur = self.options.unpack(data, cur)

		if self.flags & 0x80:
			self.param_names = []
			for i in range(self.param_count):
				cur, name = ReadU30(data, cur)
				self.param_names.append(name)

		return cur

	def pack(self):
		data = ''
		data += WriteU30(self.param_count)
		data += WriteU30(self.return_type)
		for i in range(self.param_count):
			data += WriteU30(self.param_type[i])
		data += WriteU30(self.name)
		data += WriteU8(self.flags)
		if self.flags & 0x08:
			data += self.options.pack()
		if self.flags & 0x80:
			for i in range(self.param_count):
				data += WriteU30(self.param_names[i])
		return data

class option_info():

	def unpack(self, data, cur):
		cur, self.option_count = ReadU30(data, cur)
		self.option = []
		for i in range(self.option_count):
			option = option_detail()
			cur = option.unpack(data, cur)
			self.option.append(option)
		return cur

	def pack(self):
		data = ''
		data += WriteU30(self.option_count)
		for i in range(self.option_count):
			option = self.option[i]
			data += option.pack()
		return data

class option_detail():

	kind_map = {
		0x03:'Int',
		0x04:'UInt',
		0x06:'Double',
		0x01:'Utf8',
		0x0B:'True',
		0x0A:'False',
		0x0C:'Null',
		0x00:'Undefined',
		0x08:'Namespace',
		0x16:'PackageNamespace',
		0x17:'PackageInternalNs',
		0x18:'ProtectedNamespace',
		0x19:'ExplicitNamespace',
		0x1A:'StaticProtectedNs',
		0x05:'PrivateNs'
	}

	def unpack(self, data, cur):
		cur, self.val = ReadU30(data, cur)
		cur, self.kind = ReadU8(data, cur)
		return cur

	def pack(self):
		data = ''
		data += WriteU30(self.val)
		data += WriteU8(self.kind)
		return data

class metadata_info():

	def unpack(self, data, cur):
		cur, self.name = ReadU30(data, cur)
		cur, self.item_count = ReadU30(data, cur)
		self.items = []
		for i in range(self.item_count):
			item = item_info()
			cur = item.unpack(data, cur)
			self.items.append(item)
		return cur

	def pack(self):
		data = ''
		data += WriteU30(self.name)
		data += WriteU30(self.item_count)
		for i in range(self.item_count):
			data += self.items[i].pack()
		return data

class item_info():

	def unpack(self, data, cur):
		cur, self.key = ReadU30(data, cur)
		cur, self.value = ReadU30(data, cur)
		return cur

	def pack(self):
		data = ''
		data += WriteU30(self.key)
		data += WriteU30(self.value)
		return data

class instance_info():

	def unpack(self, data, cur):
		cur, self.name = ReadU30(data, cur)
		cur, self.super_name = ReadU30(data, cur)
		cur, self.flags = ReadU8(data, cur)
		if self.flags & 0x08:
			cur, self.protectedNs = ReadU30(data, cur)
		cur, self.intrf_count = ReadU30(data, cur)
		self.interface = []
		for i in range(self.intrf_count):
			cur, interface = ReadU30(data, cur)
			self.interface.append(interface)
		cur, self.iinit = ReadU30(data, cur)
		cur, self.trait_count = ReadU30(data, cur)
		self.trait = []
		for i in range(self.trait_count):
			trait = traits_info()
			cur = trait.unpack(data, cur)
			self.trait.append(trait)
		return cur

	def pack(self):
		data = ''
		data += WriteU30(self.name)
		data += WriteU30(self.super_name)
		data += WriteU8(self.flags)
		if self.flags & 0x08:
			data += WriteU30(self.protectedNs)
		data += WriteU30(self.intrf_count)
		for i in range(self.intrf_count):
			data += WriteU30(self.interface[i])
		data += WriteU30(self.iinit)
		data += WriteU30(self.trait_count)
		for i in range(self.trait_count):
			data += self.trait[i].pack()
		return data

class traits_info():

	kind_map = {
		0:'Slot', 
		1:'Method', 
		2:'Readter', 
		3:'Setter', 
		4:'Class', 
		5:'Function', 
		6:'Const' 
	}

	attr_map = {
		1:'Final', 
		2:'Override', 
		4:'Metadata' 
	}

	class SlotT():
		def unpack(self, data, cur):
			cur, self.slot_id = ReadU30(data, cur)
			cur, self.type_name = ReadU30(data, cur)
			cur, self.vindex = ReadU30(data, cur)
			if self.vindex != 0:
				cur, self.vkind = ReadU8(data, cur)
			return cur
		def pack(self):
			data = ''
			data += WriteU30(self.slot_id)
			data += WriteU30(self.type_name)
			data += WriteU30(self.vindex)
			if self.vindex != 0:
				data += WriteU8(self.vkind)
			return data

	class ClassT():
		def unpack(self, data, cur):
			cur, self.slot_id = ReadU30(data, cur)
			cur, self.classi = ReadU30(data, cur)
			return cur
		def pack(self):
			data = ''
			data += WriteU30(self.slot_id)
			data += WriteU30(self.classi)
			return data

	class FunctionT():
		def unpack(self, data, cur):
			cur, self.slot_id = ReadU30(data, cur)
			cur, self.function = ReadU30(data, cur)
			return cur
		def pack(self):
			data = ''
			data += WriteU30(self.slot_id)
			data += WriteU30(self.function)
			return data

	class MethodT():
		def unpack(self, data, cur):
			cur, self.disp_id = ReadU30(data, cur)
			cur, self.method = ReadU30(data, cur)
			return cur
		def pack(self):
			data = ''
			data += WriteU30(self.disp_id)
			data += WriteU30(self.method)
			return data

	def unpack(self, data, cur):
		cur, self.name = ReadU30(data, cur)
		cur, self.kind = ReadU8(data, cur)
		self.kind_kind = self.kind & 0xF
		self.kind_attr = (self.kind & 0xF0) >> 4

		if self.kind_kind in (0, 6):
			self.data = self.SlotT()
		elif self.kind_kind in (4,):
			self.data = self.ClassT()
		elif self.kind_kind in (5,):
			self.data = self.FunctionT()
		elif self.kind_kind in (1, 2, 3):
			self.data = self.MethodT()
		cur = self.data.unpack(data, cur)

		if self.kind_attr & 0x04:
			cur, self.metadata_count = ReadU30(data, cur)
			self.metadata = []
			for i in range(self.metadata_count):
				cur, metadata = ReadU30(data, cur)
				self.metadata.append(metadata)

		return cur

	def pack(self):
		data = ''
		data += WriteU30(self.name)
		data += WriteU8(self.kind)
		data += self.data.pack()
		if self.kind_attr & 0x04:
			data += WriteU30(self.metadata_count)
			for i in range(self.metadata_count):
				data += WriteU30(self.metadata[i])
		return data

class class_info():

	def unpack(self, data, cur):
		cur, self.cinit = ReadU30(data, cur)
		cur, self.trait_count = ReadU30(data, cur)
		self.trait = []
		for i in range(self.trait_count):
			trait = traits_info()
			cur = trait.unpack(data, cur)
			self.trait.append(trait)
		return cur

	def pack(self):
		data = ''
		data += WriteU30(self.cinit)
		data += WriteU30(self.trait_count)
		for i in range(self.trait_count):
			data += self.trait[i].pack()
		return data

class script_info():

	def unpack(self, data, cur):
		cur, self.init = ReadU30(data, cur)
		cur, self.trait_count = ReadU30(data, cur)
		self.trait = []
		for i in range(self.trait_count):
			trait = traits_info()
			cur = trait.unpack(data, cur)
			self.trait.append(trait)
		return cur

	def pack(self):
		data = ''
		data += WriteU30(self.init)
		data += WriteU30(self.trait_count)
		for i in range(self.trait_count):
			data += self.trait[i].pack()
		return data

class method_body_info():

	def unpack(self, data, cur):

		cur, self.method = ReadU30(data, cur)
		cur, self.max_stack = ReadU30(data, cur)
		cur, self.local_count = ReadU30(data, cur)
		cur, self.init_scope_depth = ReadU30(data, cur)
		cur, self.max_scope_depth = ReadU30(data, cur)
		cur, self.code_length = ReadU30(data, cur)

		self.code = data[cur:cur+self.code_length]
		cur += self.code_length

		cur, self.exception_count = ReadU30(data, cur)
		self.exception = [] 
		for i in range(self.exception_count):
			exception = exception_info()
			cur, exception.unpack(data, cur)
			self.exception.append(exception)

		cur, self.trait_count = ReadU30(data, cur)
		self.trait = []
		for i in range(self.trait_count):
			trait = traits_info()
			cur = trait.unpack(data, cur)
			self.trait.append(trait)

		return cur

	def pack(self):
		data = ''
		data += WriteU30(self.method)
		data += WriteU30(self.max_stack)
		data += WriteU30(self.local_count)
		data += WriteU30(self.init_scope_depth)
		data += WriteU30(self.max_scope_depth)

		data += WriteU30(self.code_length)
		data += self.code

		data += WriteU30(self.exception_count)
		for i in range(self.exception_count):
			data += self.exception[i].pack()

		data += WriteU30(self.trait_count)
		for i in range(self.trait_count):
			data += self.trait[i].pack()
			
		return data

class exception_info():

	def unpack(self, data, cur):
		cur, self.begin = ReadU30(data, cur)
		cur, self.end = ReadU30(data, cur)
		cur, self.target = ReadU30(data, cur)
		cur, self.exc_type = ReadU30(data, cur)
		cur, self.var_name = ReadU30(data, cur)
		return cur

	def pack(self):
		data = ''
		data += WriteU30(self.begin)
		data += WriteU30(self.end)
		data += WriteU30(self.target)
		data += WriteU30(self.exc_type)
		data += WriteU30(self.var_name)
		return data
