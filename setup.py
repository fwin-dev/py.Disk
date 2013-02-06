from setuptools import setup, find_packages

import sys
if sys.version_info[0] >= 3 or sys.version_info <= (2,5):
	raise Exception("This module only supports Python 2.6 or 2.7")

setup(
	name = "py.Disk",
	version = "0.5.0",
	description = "Object oriented API for working with files and folders",
	author = "Jesse Cowles",
	author_email = "jcowles@indigital.net",
	url = "http://projects.indigitaldev.net/py.Disk",
	
	package_dir = {"":"src"},
	packages = find_packages("src"),
	zip_safe = False,
	install_requires = [
		"py.Lang",
		"py.OS",
		"py.Net.SSH"
	],
#	dependency_links = ["http://projects.indigitaldev.net/master#egg=py.OS-0.5.0"],
)
