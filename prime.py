import struct
import math
from bitarray import bitarray

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

def ReadEncoded32(data, cur):
	'''
	The varialbe-length encoding for u30, u32, and s32 uses one to five bytes.
	Each byte contributes its low seven bits to the value.
	return next, bytes
	'''
	val = 0
	loop = 0
	while True:
		block = struct.unpack('B', data[cur])[0]
		if block & 0x80:
			block &= 0x7F
			val |= (block << (loop * 7)) 
			loop += 1
			cur += 1
		else:
			val |= (block << (loop * 7)) 
			break

	a = bitarray(bin(val)[2:])
	align = 32 - len(a)
	a = bitarray('0') * align + a
	return cur + 1, a.tobytes()

def ReadU30(data, cur):
	'''
	Variable-length encoded 30-bit unsigned integer value
	return: next, int
	'''
	cur, bytes = ReadEncoded32(data, cur)
	val = struct.unpack('>I', bytes)[0]
	return cur, val

def ReadU32(data, cur):
	'''
	Variable-length encoded 32-bit unsigned integer value
	return: next, int
	'''
	cur, bytes = ReadEncoded32(data, cur)
	val = struct.unpack('>I', bytes)[0]
	return cur, val

def ReadS32(data, cur):
	'''
	Variable-length encoded 32-bit integer value
	return: next, int
	'''
	cur, bytes = ReadEncoded32(data, cur)
	val = struct.unpack('>i', bytes)[0]
	return cur, val

def ReadUI32(data, cur):
	'''
	Four-byte unsigned integer value
	return: next, int
	'''
	next = cur + 4
	val = struct.unpack('<I', data[cur:next])[0]
	return next, val

def ReadSI32(data, cur):
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
	return next + 1, data[cur:next] 

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

def WriteEncoded32(val, signed):
	'''
	The varialbe-length encoding for u30, u32, and s32 uses one to five bytes.
	Each byte contributes its low seven bits to the value.
	'''
	data = ''
	a = None
	if val < 0:
		a = bitarray(bin(val)[3:])
	else:
		a = bitarray(bin(val)[2:])

	if signed and val < 0:
		align = 32 - len(a)
		a = align * bitarray('1') + a

	while len(a) > 7:
		block = bitarray('1') + a[-7:]
		a = a[:-7]
		data += block.tobytes()

	align = 8 - len(a)
	block = align * bitarray('0') + a
	data += block.tobytes()
	return data

def WriteU30(val):
	'''
	Variable-length encoded 30-bit unsigned integer value
	'''
	return WriteEncoded32(val, False)

def WriteU32(val):
	'''
	Variable-length encoded 32-bit unsigned integer value
	'''
	return WriteEncoded32(val, False)

def WriteS32(val):
	'''
	Variable-length encoded 32-bit integer value
	'''
	return WriteEncoded32(val, True)

def WriteUI32(val):
	'''
	Four-byte unsigned integer value
	'''
	return struct.pack('<I', val)

def WriteSI32(val):
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
	data += b'\x00'
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
		cur, length = ReadUI32(data, cur)
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
		data += WriteUI32(tagLength)
	else:
		tagCodeAndLength |= tagLength
		data += WriteU16(tagCodeAndLength)
	return data

def ReadRect(data, cur):
	'''
	return: next, rect[left, top, right, bottom]
	'''
	nbits = struct.unpack('>B', data[cur])[0]
	nbits = nbits >> 3
	nbytes = (nbits * 4 + 5) / 8.0
	nbytes = int(math.ceil(nbytes))
	next = cur + nbytes
	a = bitarray(endian='big')
	a.frombytes(data[cur:next])
	rect = [] 
	for i in range(4):
		begin = 5 + i * nbits
		end = begin + nbits
		num = a[begin:end]
		num = int(num.to01(), 2)
		rect.append(num)
	return next, rect

def WriteRect(rect):
	'''
	rect:[left, top, right, bottom]
	'''
	mx = max(rect)
	mxBits = 1
	while mx > 0:
		mx >>= 1
		mxBits += 1

	data = bitarray(bin(mxBits + 0x80)[2:])
	data = data[-5:]
	for i in range(4):
		temp = bitarray(bin(rect[i])[2:])
		l = len(temp)
		if l < mxBits:
			temp = bitarray('0' * (mxBits - l)) + temp
		data += temp

	l = 5 + 4 * mxBits
	if l & 0x7:
		align = ((l >> 3 + 1) << 3) - l
		data += bitarray('0' * align)

	return data.tobytes()
