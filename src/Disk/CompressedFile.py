import Disk.Local

import zipfile as zipfile_module
import os, os.path

class UnrecognizedFormat(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

class ZipFile(object):
	"""Improvement of built-in python module zipfile.Zipfile"""
	def __init__(self, zipFile):
		"""
		@type zipFile: Can be a file-like object (including any File instance), a FilePath instance, or a string.
		"""
		self.zipFile = zipFile
		if isinstance(self.zipFile, basestring):
			self.zipFile = Disk.Local.FilePath(self.zipFile)
		if isinstance(self.zipFile, Disk._base.FilePath):
			self.zipFile = self.zipFile.asFile(mode="rb")
	
	def extract(self, extractDir):
		"""
		Extract the ZipFile instance to extractDir.
		
		@type extractDir: Can be a FolderPath instance or a string
		
		Sets chmod permissions for each file from the zip to the extracted one, which the built-in python zipfile module doesn't do by default.
		Source: Adapted from https://bitbucket.org/mumak/distribute/src/2f489b41a507/setuptools/archive_util.py
		"""
		if not zipfile_module.is_zipfile(self.zipFile):
			raise UnrecognizedFormat(str(self.zipFile) + " is not a zip file")
		if isinstance(extractDir, basestring):
			extractDir = Disk.Local.FolderPath(extractDir)
		
		zipfile = zipfile_module.ZipFile(self.zipFile)
		try:
			for info in zipfile.infolist():
				name = info.filename
	
				# don't extract absolute paths or ones with .. in them
				if name.startswith("/") or ".." in name:
					continue
				
				if name.endswith("/"):	# directory
					destPath = extractDir.joinFolder(*name.split("/"))
					destPath.dirname().mkdirs()
				else:	# file
					destPath = extractDir.joinFile(*name.split("/"))
					destPath.dirname().mkdirs()
					data = zipfile.read(info.filename)
					f = open(destPath, "wb")
					try:
						f.write(data)
					finally:
						f.close()
						del data
				
				unix_attributes = info.external_attr >> 16
				if unix_attributes:
					os.chmod(destPath, unix_attributes)
		finally:
			zipfile.close()
