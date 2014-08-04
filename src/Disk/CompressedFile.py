import Disk.Local

import zipfile as zipfile_module
from datetime import datetime
import calendar
import os

class UnrecognizedFormat(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

class ZipFile(object):
	"""Improvement of built-in python module zipfile.Zipfile"""
	def __init__(self, zipFile):
		"""
		@type zipFile: Can be a file-like object (including any File instance), a FilePath instance, or a string.
		"""
		self._zipFile = zipFile
		if isinstance(self._zipFile, basestring):
			self._zipFile = Disk.Local.FilePath(self._zipFile)
		if isinstance(self._zipFile, Disk._base.FilePath):
			self._zipFile = self._zipFile.asFile(mode="rb")
	
	def extract(self, extractDir, shouldCopyDates):
		"""
		Extract the ZipFile instance to extractDir.
		
		@type extractDir: Can be a FolderPath instance or a string
		
		Sets chmod permissions for each file from the zip to the extracted one, which the built-in python zipfile module doesn't do by default.
		Source: Adapted from https://bitbucket.org/mumak/distribute/src/2f489b41a507/setuptools/archive_util.py
		"""
		with self._zipFile:
			if not zipfile_module.is_zipfile(self._zipFile):
				raise UnrecognizedFormat(str(self._zipFile) + " is not a zip file")
			if isinstance(extractDir, basestring):
				extractDir = Disk.Local.FolderPath(extractDir)
		
		self._zipFile.open()
		zipfile = zipfile_module.ZipFile(self._zipFile)
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
					with destPath.asFile("wb") as f:
						f.write(data)
					del data
				
				if shouldCopyDates:
					modTime_int = calendar.timegm(datetime(*info.date_time).timetuple())
					destPath.utime(modTime_int, modTime_int)
				
				unix_attributes = info.external_attr >> 16
				if unix_attributes:
					destPath.chmod(unix_attributes)
		finally:
			zipfile.close()
			self._zipFile.close()
