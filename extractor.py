import json
from abcutils import *
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
		clsName, nsi = extractMultiname(abc, instance.name)
		pkgName, visibility = extractNamespace(abc, nsi)

		pkg = None
		if pkgName in self.pkgs:
			pkg = self.pkgs[pkgName]
		else:
			pkg = {'name':pkgName, 'classes':{}, 'obfuscate':True}
			self.pkgs[pkgName] = pkg
		if not rule['package']:
			pkg['obfuscate'] = False

		clss = pkg['classes']
		if clsName in clss:
			raise Exception('Class "' + clsName + '" already existed!\nIn package "' + pkgName + '"')

		superName = None
		superPkgName = None
		if instance.super_name != 0:
			superName, nsi = extractMultiname(abc, instance.super_name)
			superPkgName, _ = extractNamespace(abc, nsi)

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
		funcName, nsi = extractMultiname(abc, trait.name)
		_, visibility = extractNamespace(abc, nsi)
		obfuscate = rule[visibility + '_function']
		method = abc.method[trait.data.method]
		typeName = '*'
		typePkg = '*'
		if method.return_type != 0:
			typeName, nsi = extractMultiname(abc, method.return_type)
			typePkg, _ = extractNamespace(abc, nsi)

		func = {
			'name':funcName,
			'visibility':visibility,
			'type_name':typeName,
			'type_pkg':typePkg,
			'obfuscate':obfuscate
		}

		funcs = cls['functions']
		funcs[funcName] = func

	def extractProperty(self, abc, trait, rule, cls):
		propName, nsi = extractMultiname(abc, trait.name)
		_, visibility = extractNamespace(abc, nsi)
		obfuscate = rule[visibility + '_property']

		typeName = '*'
		typePkg = '*'
		if trait.data.type_name != 0:
			typeName, nsi = extractMultiname(abc, trait.data.type_name)
			typePkg, _ = extractNamespace(abc, nsi)

		prop = {
			'name':propName,
			'visibility':visibility,
			'type_name':typeName,
			'type_pkg':typePkg,
			'obfuscate':obfuscate
		}

		props = cls['properties']
		props[propName] = prop
