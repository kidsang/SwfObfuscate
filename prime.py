import struct

def ReadU8(data, cur):
	'''
	One-byte unsigned integer value
	return: next, int
	'''
	val = struct.unpack('B', data[cur])[0]
	return cur + 1, val

def ReadU16(data, cur):
	'''
	Two-byte unsigned integer value
	return: next, int
	'''
	next = cur + 2
	val = struct.unpack('<H', data[cur:next])[0]
	return next, val

def ReadS24(data, cur):
	'''
	Three-byte signed integer value
	return: next, int
	'''
	cur, lo = ReadU16(data, cur)
	hi = struct.unpack('b', data[cur])[0] 
	val = (hi << 8) | lo
	
def ReadU30(data, cur):
	'''
	Variable-length encoded 30-bit unsigned integer value
	return: next, int
	'''
	while True:

		val = struct.unpack('B', data[cur])[0]
		if not (val & 0x80):
			break

		cur += 1
		val = (val & 0x7f) | struct.unpack('B', data[cur])[0] << 7
		if not (val & 0x4000):
			break

		cur += 1
		val = (val & 0x3fff) | struct.unpack('B', data[cur])[0] << 14
		if not (val & 0x200000):
			break

		cur += 1
		val = (val & 0x1fffff) | struct.unpack('B', data[cur])[0] << 21
		if not (val & 0x10000000):
			break

		cur += 1
		val = (val & 0x0fffffff) | struct.unpack('B', data[cur])[0] << 28
		break

	return cur + 1, val

def ReadU32(data, cur):
	'''
	Four-byte unsigned integer value
	return: next, int
	'''
	next = cur + 4
	val = struct.unpack('<I', data[cur:next])[0]
	return next, val

def ReadS32(data, cur):
	'''
	Four-byte signed integer value
	return: next, int
	'''
	next = cur + 4
	val = struct.unpack('<i', data[cur:next])[0]
	return next, val

def ReadD64(data, cur):
	'''
	Eight-byte IEEE-754 floating point value
	return: next, float
	'''
	next = cur + 8
	val = struct.unpack('<d', data[cur:next])[0]
	return next, val

def ReadCString(data, cur):
	'''
	Variable-length UTF-8 encoded string end with 0
	return: next, string
	'''
	next = cur
	while data[next] != b'\x00':
		next += 1
	next += 1
	return next, data[cur:next] 

def WriteU8(val):
	'''
	One-byte unsigned integer value
	'''
	return struct.pack('B', val)

def WriteU16(val):
	'''
	Two-byte unsigned integer value
	'''
	return struct.pack('<H', val)

def WriteS24(val):
	'''
	Three-byte signed integer value
	'''
	data = struct.pack('<i', val)
	return data[:3]
	
def WriteU30(val):
	'''
	Variable-length encoded 30-bit unsigned integer value
	'''
	data = ''
	while val >= 0x3F:
		lo = (val & 0x3F) | 0x80
		val = val >> 7
		data += struct.pack('B', lo)
	lo = val & 0x3F
	data += struct.pack('B', lo)
	return data

def WriteU32(val):
	'''
	Four-byte unsigned integer value
	'''
	return struct.pack('<I', val)

def WriteS32(val):
	'''
	Four-byte signed integer value
	'''
	return struct.pack('<i', val)

def WriteD64(val):
	'''
	Eight-byte IEEE-754 floating point value
	'''
	return struct.pack('<d', val)

def WriteCString(val):
	'''
	Variable-length UTF-8 encoded string end with 0
	'''
	data = struct.pack(str(len(val)) + 's', val)
	return data

def ReadTagHeader(data, cur):
	'''
	Swf file tag header
	return: next:int, tagCode:int, tagLength:int
	'''
	cur, tagCodeAndLength = ReadU16(data, cur)
	length = tagCodeAndLength & 0x3F
	tagCode = (tagCodeAndLength & 0xFFC0) >> 6
	if length == 0x3F:
		cur, length = ReadU32(data, cur)
	return cur, tagCode, length

def WriteTagHeader(tagCode, tagLength):
	'''
	Swf file tag header
	'''
	data = ''
	tagCodeAndLength = tagCode << 6
	if tagLength >= 0x3F:
		tagCodeAndLength |= 0x3F
		data += WriteU16(tagCodeAndLength)
		data += WriteU32(tagLength)
	else:
		tagCodeAndLength |= tagLength
		data += WriteU16(tagCodeAndLength)
	return data
