from ..TempFile import NamedSecureTempFile
from .. import Local

import sys, fileinput, re

class ParseException(Exception):
	def __init__(self, message=""):
		self.message = message
	def __str__(self):
		return self.message

class _ConfigLine:
	def __init__(self, line, commentChar='#', assignChar='='):
		"""assignChar	str:	can be None"""
		self.line = line
		self.commentChar = commentChar
		self.assignChar = assignChar
		
		temp = self.line.strip()
		if len(temp) > 0 and temp[0] == self.commentChar:
			temp = temp[1:]
			self.isCommentedOut = True
		else:
			self.isCommentedOut = False
		
		if assignChar != None:
			temp = temp.split(self.assignChar, 1)
			self.optionName = temp[0]
			temp = temp[1]
		else:
			self.optionName = None
		
		temp = re.split("(\s*" + re.escape(self.commentChar) + ".*)$", temp, 1)
		if self.optionName != None:
			self.optionValue = temp[0].strip()
		else:
			self.optionName = temp[0].strip()
			self.optionValue = None
		
		if len(temp) > 1:
			self.endLine = temp[1]
			if self.endLine == "":
				self.endLine = None
		else:
			self.endLine = None
	
	def __str__(self):
		return self.line

def changeConfig(filePath, newLine, commentChar='#', assignChar=' ', sectionName=None, sectionMatch='['):
	"""@see _changeConfig()"""
	if isinstance(filePath, basestring):
		filePath = Local.FilePath(filePath)
	backupFile = NamedSecureTempFile(delete=False)
	filePath.copy(backupFile, shouldCopyDates=True)
	try:
		return _changeConfig(filePath, newLine, commentChar, assignChar, sectionName, sectionMatch)
	except:
		backupFile.move(filePath)
		raise Exception("Exception occurred during a configuration change - config file not modified")

def _changeConfig(_file, newLine, commentChar="#", assignChar=" ", sectionName=None, sectionMatch="["):
	"""
	Changes a config file line in the format `#OptionName foo` (format can be changed with parameters) under specified section.
	
	@param newLine		str:	The new/changed line to write to the configuration file.
	@param commentChar	str:	The character used for commenting out lines. Used for interpreting the config file.
	@param assignChar	str:	The character used between the key and value. Used for interpreting the config file.
	@param sectionName	str:	The section name where the newLine should be located. `None` indicates there are no sections in the config file.
	@param sectionMatch	str:	The character to the left of the section name used by the config file. Usually, section names are enclosed with `[]`.
	@return list: List containing all of the following that apply:
		0	If setting name was encountered in the file and it was uncommented
		1	If setting name was encountered in the file and it was commented out
		2	If setting name and value were added by this function
		3	If setting value was changed by this function """
	newLine = _ConfigLine(newLine + "\n", commentChar, assignChar)
	
	returnCode = []
	inSection = False
	for line in fileinput.input(_file, inplace=1):
		if sectionName != None:
			if line.startswith(sectionMatch):
				if line.startswith(sectionMatch + sectionName):
					inSection = True
				else:
					inSection = False
				sys.stdout.write(line)
				continue
			if not inSection:
				sys.stdout.write(line)
				continue
		
		try:
			parsedOldLine = _ConfigLine(line, commentChar, assignChar)
		except ParseException:
			sys.stdout.write(line)
			continue
		if parsedOldLine.optionName != newLine.optionName:
			sys.stdout.write(line)
			continue
		if len(returnCode) != 0:
			continue	# don't write line
		
		if newLine.endLine == None and parsedOldLine.endLine != None:
			newLine.endLine = parsedOldLine.endLine
		
		sys.stdout.write(str(newLine))	# writes new line in place of old line
		if parsedOldLine.isCommentedOut:
			returnCode.append(1)
		else:
			returnCode.append(0)
		if parsedOldLine.optionValue != newLine.optionValue:
			returnCode.append(3)
	
	if len(returnCode) == 0:
		with open(_file, 'a') as f:
			f.write(str(newLine))
		returnCode = [2]
	
	return returnCode
