# -*- coding: UTF-8 -*-
import gettext
import locale
import os

from Tools.Directories import SCOPE_LANGUAGE, resolveFilename

class Language:
	def __init__(self):
		gettext.install('enigma2', resolveFilename(SCOPE_LANGUAGE, ""), unicode=0, codeset="utf-8")
		gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
		gettext.textdomain("enigma2")
		self.activeLanguage = 0
		self.catalog = None
		self.lang = {}
		self.InitLang()
		self.callbacks = []
		
	def InitLang(self):
		self.langlist = []
		self.langlistselection = []
		# FIXME make list dynamically
		# name, iso-639 language, iso-3166 country. Please don't mix language&country!
		self.addLanguage("English",     "en", "EN", "ISO-8859-15")
		self.addLanguage("Català",      "ca", "AD", "ISO-8859-15")
		self.addLanguage("Español",     "es", "ES", "ISO-8859-15")
		

	def addLanguage(self, name, lang, country, encoding):
		try:
			self.lang[str(lang + "_" + country)] = ((name, lang, country, encoding))
			self.langlist.append(str(lang + "_" + country))
		except:
			print "Language " + str(name) + " not found"
		self.langlistselection.append((str(lang + "_" + country), name))

	def activateLanguage(self, index):
		try:
			if index not in self.lang:
				print "Selected language %s does not exist, fallback to en_EN!" % index
				index = "es_ES"
			lang = self.lang[index]
			print "Activating language " + lang[0]
			self.catalog = gettext.translation('enigma2', resolveFilename(SCOPE_LANGUAGE, ""), languages=[index], fallback=True)
			self.catalog.install(names=("ngettext", "pgettext"))
			self.activeLanguage = index
			for x in self.callbacks:
				x()
		except:
			print "Error in activating language!"
		# NOTE: we do not use LC_ALL, because LC_ALL will not set any of the categories, when one of the categories fails.
		# We'd rather try to set all available categories, and ignore the others
		for category in [locale.LC_CTYPE, locale.LC_COLLATE, locale.LC_TIME, locale.LC_MONETARY, locale.LC_MESSAGES, locale.LC_NUMERIC]:
			try:
				locale.setlocale(category, (self.getLanguage(), 'UTF-8'))
			except:
				pass
		# HACK: sometimes python 2.7 reverts to the LC_TIME environment value, so make sure it has the correct value
		os.environ["LC_TIME"] = self.getLanguage() + '.UTF-8'
		os.environ["LANGUAGE"] = self.getLanguage() + '.UTF-8'
		os.environ["GST_SUBTITLE_ENCODING"] = self.getGStreamerSubtitleEncoding()

	def activateLanguageIndex(self, index):
		if index < len(self.langlist):
			self.activateLanguage(self.langlist[index])

	def getLanguageList(self):
		return [ (x, self.lang[x]) for x in self.langlist ]

	def getLanguageListSelection(self):
		return self.langlistselection

	def getActiveLanguage(self):
		return self.activeLanguage

	def getActiveCatalog(self):
		return self.catalog

	def getActiveLanguageIndex(self):
		idx = 0
		for x in self.langlist:
			if x == self.activeLanguage:
				return idx
			idx += 1
		return None

	def getLanguage(self):
		try:
			return str(self.lang[self.activeLanguage][1]) + "_" + str(self.lang[self.activeLanguage][2])
		except:
			return ''

	def getGStreamerSubtitleEncoding(self):
		try:
			return str(self.lang[self.activeLanguage][3])
		except:
			return 'ISO-8859-15'

	def addCallback(self, callback):
		self.callbacks.append(callback)

language = Language()
