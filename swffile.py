import zlib
from prime import *
from abcfile import ABCFile

class SWFFile():

	def unpack(self, data):
		self.signature = data[:3]
		cur, self.version = ReadU8(data, 3)
		cur, file_length = ReadU32(data, 4)
		data = data[8:]

		if self.signature == 'CWS':
			data = zlib.decompress(data)

		cur = 0
		cur, self.frame_size = ReadRect(data, cur)
		cur, self.frame_rate = ReadU16(data, cur)
		cur, self.frame_count = ReadU16(data, cur)

		self.trunks = []
		self.abcIndices = []
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
			else:
				self.trunks.append(data[begin:end])
			cur = end
			i += 1

	def pack(self):
		data = ''
		data += WriteRect(self.frame_size)
		data += WriteU16(self.frame_rate)
		data += WriteU16(self.frame_count)

		for i in range(len(self.trunks)):
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
		header += WriteU32(file_length)
		data =  header + data

		return data

	def abcFiles(self):
		return [self.trunks[i] for i in self.abcIndices]