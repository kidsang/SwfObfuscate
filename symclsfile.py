from prime import *

class SymbolClassFile():

	def unpack(self, data, cur):
		cur, self.tagCode, length = ReadTagHeader(data, cur)
		cur, self.num_symbols = ReadUI16(data, cur)

		self.tag = []
		self.name = []
		for i in xrange(self.num_symbols):
			cur, tag = ReadUI16(data, cur)
			cur, name = ReadCString(data, cur)
		self.tag.append(tag)
		self.name.append(name)

		return cur

	def pack(self):
		data = ''

		data += WriteUI16(self.num_symbols)
		for i in xrange(self.num_symbols):
			data += WriteUI16(self.tag[i])
			data += WriteCString(self.name[i])

		data = WriteTagHeader(self.tagCode, len(data)) + data

		return data
