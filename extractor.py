import json
from abcfile import *

class Extractor():

	def __init__(self, ruleFilePath):
		self.pkgs = {}
		self.loadRules(ruleFilePath)

	def getJson(self, pretty = True):
		if pretty:
			return json.dumps(self.pkgs, sort_keys=True, indent=4, separators=(',', ': '))
		else:
			return json.dumps(self.pkgs)

	def exportToFile(self, fileName):
		f = open(fileName, 'w')
		f.write(self.getJson())
		f.close()

	def loadRules(self, ruleFilePath):
		f = open(ruleFilePath, 'r')
		jsonStr = f.read()
		f.close()
		self.rules = json.loads(jsonStr)
		self.defaultRules = self.rules['default']
		self.rules = self.rules['rules']

	def buildRule(self, fileName):
		fullRule = {}
		if fileName in self.rules:
			rule = self.rules[fileName]
			for key in self.defaultRules.keys():
				if key in rule:
					fullRule[key] = rule[key]
				else:
					fullRule[key] = self.defaultRules[key]
		else:
			fullRule = self.defaultRules
		return fullRule

	def extract(self, abc, fileName):
		rule = self.buildRule(fileName)
		self.extractInstances(abc, rule)

	def extractInstances(self, abc, rule):
		instances = abc.instance
		for instance in instances:
			cls = self.extractClass(abc, instance, rule)
			traits = instance.trait
			for trait in traits:
				kind = trait.kind_kind
				if kind == 0:
					self.extractProperty(abc, trait, rule, cls)
				elif kind in (1, 2, 3, 5):
					self.extractFunction(abc, trait, rule, cls)

	def extractClass(self, abc, instance, rule):
		clsName, nsi = self.extractMultiname(abc, instance.name)
		pkgName, visibility = self.extractNamespace(abc, nsi)

		pkg = None
		if pkgName in self.pkgs:
			pkg = self.pkgs[pkgName]
		else:
			pkg = {'name':pkgName, 'classes':{}}
			self.pkgs[pkgName] = pkg

		clss = pkg['classes']
		if clsName in clss:
			raise Exception('Class "' + clsName + '" already existed!\nIn package "' + pkgName + '"')

		superName = None
		superPkgName = None
		if instance.super_name != 0:
			superName, nsi = self.extractMultiname(abc, instance.super_name)
			superPkgName, _ = self.extractNamespace(abc, nsi)

		obfuscate = rule[visibility + '_class']

		cls = {
			'name':clsName,
			'super_package':superPkgName,
			'super_name':superName,
			'obfuscate':obfuscate,
			'functions':{},
			'properties':{}
		}

		clss[clsName] = cls
		return cls

	def extractFunction(self, abc, trait, rule, cls):
		funcName, nsi = self.extractMultiname(abc, trait.name)
		_, visibility = self.extractNamespace(abc, nsi)
		obfuscate = rule[visibility + '_function']

		func = {
			'name':funcName,
			'visibility':visibility,
			'obfuscate':obfuscate
		}

		funcs = cls['functions']
		funcs[funcName] = func

	def extractProperty(self, abc, trait, rule, cls):
		propName, nsi = self.extractMultiname(abc, trait.name)
		_, visibility = self.extractNamespace(abc, nsi)
		obfuscate = rule[visibility + '_property']

		prop = {
			'name':propName,
			'visibility':visibility,
			'obfuscate':obfuscate
		}

		props = cls['properties']
		props[propName] = prop

	def extractMultiname(self, abc, mni):
		pool = abc.constant_pool
		mn = pool.multiname[mni]
		data = mn.data
		name = pool.string[data.name].utf8
		nsi = data.ns
		return name, nsi

	def extractNamespace(self, abc, nsi):
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
