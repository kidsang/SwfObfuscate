import json
from abcutils import *

class ABCObfuscator():

	def __init__(self, classInfo):
		if isinstance(classInfo, str):
			f = open(classInfo, 'r')
			jsonStr = f.read()
			f.close()
			self.info = json.loads(jsonStr)
		else:
			self.info = classInfo

		self.pubPrime = ['!', '@', '#', '$', '%', '_', '^', '&']
		self.pubIndices = [-1]
		self.priPrime = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
		self.priIndices = [-1]

		self.buildPublicReplaceMap()

	def buildPublicReplaceMap(self):
		pub_rep_map = {}
		non_rep_set = set()

		for pkgName in self.info:
			pkg = self.info[pkgName]
			if pkg['obfuscate']:
				if pkgName not in pub_rep_map:
					pub_rep_map[pkgName] = self.genID()
			else:
				non_rep_set.add(pkgName)

			clss = pkg['classes']
			for clsName in clss:
				cls = clss[clsName]
				if cls['obfuscate']:
					if clsName not in pub_rep_map:
						pub_rep_map[clsName] = self.genID()
				else:
					non_rep_set.add(clsName)
					
				funcs = cls['functions']
				for funcName in funcs:
					func = funcs[funcName]
					if func['visibility'] in ('public', 'protected'):
						if func['obfuscate']:
							if funcName not in pub_rep_map:
								pub_rep_map[funcName] = self.genID()
						else:
							non_rep_set.add(funcName)
					
				props = cls['properties']
				for propName in props:
					prop = props[propName]
					if prop['visibility'] in ('public', 'protected'):
						if prop['obfuscate']:
							if propName not in pub_rep_map:
								pub_rep_map[propName] = self.genID()
						else:
							non_rep_set.add(propName)

		self.pub_rep_map = pub_rep_map
		self.non_rep_set = non_rep_set

	def buildPrivateReplaceMap(self, cls):
		self.priIndices = [-1]
		pri_rep_map = {}
		pub_rep_map = self.pub_rep_map

		funcs = cls['functions']
		for funcName in funcs:
			func = funcs[funcName]
			if func['visibility'] == 'private':
				if func['obfuscate']:
					if funcName not in pub_rep_map and funcName not in pri_rep_map:
						pri_rep_map[funcName] = self.genID(False)
			
		props = cls['properties']
		for propName in props:
			prop = props[propName]
			if prop['visibility'] == 'private':
				if prop['obfuscate']:
					if propName not in pub_rep_map and propName not in pri_rep_map:
						pri_rep_map[propName] = self.genID(False)

		self.pri_rep_map = pri_rep_map

	def genID(self, public = True):
		indices = self.genIndices(public)
		newID = ''
		for i in indices:
			if public:
				newID += self.pubPrime[i]
			else:
				newID += self.priPrime[i]
		return newID

	def genIndices(self, public):
		indices = None
		prime = None
		if public:
			indices = self.pubIndices
			prime = self.pubPrime
		else:
			indices = self.priIndices
			prime = self.priPrime
		total = len(prime)
		bit = len(indices) - 1
		while True:
			indices[bit] += 1
			if indices[bit] < total:
				break
			else:
				indices[bit] = 0
				if bit == 0:
					indices.append(0)
					break
				else:
					bit -= 1

		return indices

	def processDoABC(self, abc):
		self.processPrivate(abc)
		self.processPublic(abc)

	def processPublic(self, abc):
		pool = abc.constant_pool
		string = pool.string
		for i in xrange(1, len(string)):
			origin = string[i].utf8
			l = len(origin)
			if l < 1:
				continue
			if origin not in self.non_rep_set and origin in self.pub_rep_map:
				replace = self.pub_rep_map[origin]
				string[i].utf8 = replace
				string[i].size = len(replace)
				# print origin, ':', replace

	def processPrivate(self, abc):
		pool = abc.constant_pool
		string = pool.string
		instances = abc.instance
		for instance in instances:
			clsName, nsi = extractMultiname(abc, instance.name)
			pkgName, _ = extractNamespace(abc, nsi)

			pkg = self.info[pkgName]
			cls = pkg['classes'][clsName]
			self.buildPrivateReplaceMap(cls)

			for i in xrange(1, len(string)):
				origin = string[i].utf8
				l = len(origin)
				if l < 1:
					continue
				if origin not in self.non_rep_set and origin in self.pri_rep_map:
					replace = self.pri_rep_map[origin]
					string[i].utf8 = replace
					string[i].size = len(replace)
					print origin, ':', replace


	def obfuscateInstance(self, abc, instance):
		cls = self.obfuscateClass(abc, instance, rule)
		traits = instance.trait
		for trait in traits:
			kind = trait.kind_kind
			if kind == 0:
				self.obfuscateProperty(abc, trait, rule, cls)
			elif kind in (1, 2, 3, 5):
				self.obfuscateFunction(abc, trait, rule, cls)

	def processSymbolClass(self, symcls):
		for i in xrange(symcls.num_symbols):
			name = symcls.name[i]
			pkgName = ''
			clsName = name
			index = name.rfind('.')
			if index != -1:
				pkgName = name[:index]
				clsName = name[index + 1:]

			pkg = self.info[pkgName]
			obfuscatePkg = pkg['obfuscate']
			if obfuscatePkg:
				pkgName = self.pub_rep_map[pkgName]

			cls = pkg['classes'][clsName]
			obfuscateCls = cls['obfuscate']
			if obfuscateCls:
				clsName = self.pub_rep_map[clsName]

			name = clsName
			if pkgName != '':
				name = pkgName + '.' + name
			symcls.name[i] = name

