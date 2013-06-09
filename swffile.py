import zlib
from prime import *
from abcfile import ABCFile

class SWFFile():

	def unpack(self, data):
		self.signature = data[:3]
		self.uncompressed = data[:8]
		data = data[8:]

		if self.signature == 'CWS':
			data = zlib.decompress(data)

		self.trunks = []
		self.abcIndices = []
		totalLen = len(data)
		cur = 0
		i = 0
		while cur <= totalLen:
			begin = cur
			cur, tagCode, tagLength = ReadTagHeader(data, cur)
			end = cur + tagLength
			if tagCode == 82: # doABC
				abcFile = ABCFile()
				abcfile.unpack(data[begin:end], 0)
				self.trunks.append(abcFile)
				self.abcIndices.append[i]
			else:
				self.trunks.append(data[begin:end])
			cur = end
			i += 1

	def pack(self):
		data = ''

		for i in range(len(self.trunks)):
			trunk = self.trunks[i]
			if getattr(trunk, 'pack', None):
				data += trunk.pack()
			else:
				data += trunk

		if self.signature == 'CWS':
			data = zlib.compress(data)

		data = self.uncompressed + data

		return data
