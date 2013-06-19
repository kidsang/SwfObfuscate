import zlib
from prime import *
from abcfile import ABCFile
from symclsfile import SymbolClassFile

class SWFFile():

	def unpack(self, data):
		self.signature = data[:3]
		cur, self.version = ReadU8(data, 3)
		cur, file_length = ReadUI32(data, 4)
		data = data[8:]

		if self.signature == 'CWS':
			data = zlib.decompress(data)

		cur = 0
		cur, self.frame_size = ReadRect(data, cur)
		cur, self.frame_rate = ReadUI16(data, cur)
		cur, self.frame_count = ReadUI16(data, cur)

		self.trunks = []
		self.abcIndices = []
		self.symclsIndices = []
		totalLen = len(data)
		i = 0
		while cur < totalLen:
			begin = cur
			cur, tagCode, tagLength = ReadTagHeader(data, cur)
			end = cur + tagLength
			if tagCode == 82: # doABC
				abcFile = ABCFile()
				abcFile.unpack(data[begin:end], 0)
				self.trunks.append(abcFile)
				self.abcIndices.append(i)
			elif tagCode == 76: # Symbol Class
				symclsFile = SymbolClassFile()
				symclsFile.unpack(data[begin:end], 0)
				self.trunks.append(symclsFile)
				self.symclsIndices.append(i)
			else:
				self.trunks.append(data[begin:end])
			cur = end
			i += 1

	def pack(self):
		data = ''
		data += WriteRect(self.frame_size)
		data += WriteUI16(self.frame_rate)
		data += WriteUI16(self.frame_count)

		for i in xrange(len(self.trunks)):
			trunk = self.trunks[i]
			if getattr(trunk, 'pack', None):
				data += trunk.pack()
			else:
				data += trunk

		file_length = len(data) + 8

		if self.signature == 'CWS':
			data = zlib.compress(data)

		header = self.signature
		header += WriteU8(self.version)
		header += WriteUI32(file_length)
		data =  header + data

		return data

	def abcFiles(self):
		return [self.trunks[i] for i in self.abcIndices]

	def symclsFiles(self):
		return [self.trunks[i] for i in self.symclsIndices]
