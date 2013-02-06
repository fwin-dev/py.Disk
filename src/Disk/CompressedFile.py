import zipfile
import os, os.path

class UnrecognizedFormat(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

class ZipFile:
	"""Improvement of built-in python module zipfile.Zipfile"""
	def __init__(self, zipFilePath):
		self.zipFilePath = zipFilePath
	def _ensureDirectory(self, path):
		"""Ensure that the parent directory of `path` exists"""
		dirname = os.path.dirname(path)
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
	def extract(self, extractDir):
		"""
		Extract zipFilePath to extractDir.
		
		Sets chmod permissions for each file from the zip to the extracted one, which the built-in python zipfile module doesn't do by default.
		Source: Adapted from https://bitbucket.org/mumak/distribute/src/2f489b41a507/setuptools/archive_util.py
		"""
		if not zipfile.is_zipfile(self.zipFilePath):
			raise UnrecognizedFormat(str(self.zipFilePath) + " is not a zip file")
		
		z = zipfile.ZipFile(self.zipFilePath)
		try:
			for info in z.infolist():
				name = info.filename
	
				# don't extract absolute paths or ones with .. in them
				if name.startswith("/") or ".." in name:
					continue
				
				target = os.path.join(extractDir, *name.split("/"))
				if name.endswith("/"):	# directory
					self._ensureDirectory(target)
				else:	# file
					self._ensureDirectory(target)
					data = z.read(info.filename)
					f = open(target,"wb")
					try:
						f.write(data)
					finally:
						f.close()
						del data
				unix_attributes = info.external_attr >> 16
				if unix_attributes:
					os.chmod(target, unix_attributes)
		finally:
			z.close()
