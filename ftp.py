
# Sublime FTP sender
#
# send current file to ftp
#
# Config:
# Preferences - Key Bindings User
# { "keys": ["ctrl+f+p"], "command": "subl-ftp"}
#

# sublime modules
import sublime
import sublime_plugin

# python modules
import os
import glob
import ftplib
import sys
import json
import re


class Ftp:
	#
	connection = False
	#
	curr_path  = ""

	def __init__(self, host, login, passwd):
		try:
			self.connection = ftplib.FTP(host, login, passwd)
		except Exception:
			pass

	def checkConn(self):
		return self.connection != False

	def mkdir(self, dir_name):
		self.connection.mkd(dir_name)

	def mv(self, subdir):
		self.connection.cwd(subdir)

	def set_path(self, path):
		self.curr_path = path

	def go_dir(self, path):
		pth = path.split('/')

		for subdir in pth:
			if not subdir in self.connection.nlst():
				self.mkdir(subdir)
			self.mv(subdir)

		self.set_path(path)

	def up(self, file_name):
		fl = open(file_name, "rb")
		file_name = file_name.split('/')
		final_file_name = file_name[-1]
		self.connection.storbinary('STOR '+ final_file_name, fl)
		sublime.status_message('Stored file ' + str(final_file_name) + ' to FTP server')
		fl.close()




# sublime filecommand plugin
class FtpCommand(sublime_plugin.TextCommand):

	# run plugin method on press keys combination
	def run(self, edit, **args):
		# current folder
		if not 'folder' in args:
			sublime.status_message("ERROR! Put your projects base path")
			return

		tmp_dir        = args['folder']
		active_file    = sublime.active_window().active_view().file_name()
		folder         = os.path.dirname(active_file)
		folder         = re.sub(tmp_dir, '', folder)

		project_folder = tmp_dir + folder.split('/')[0]
		folder         = re.sub(folder.split('/')[0], '', folder)

		try:
			json_data = open( project_folder + '/_ftp.json').read()
		except Exception:
			return

		config          = json.loads(json_data)
		ftp_base_folder = config['ftp_base']

		ftp = Ftp(config['host'], config['login'], config['passwd'])

		if not ftp.checkConn():
			sublime.status_message("ERROR! Missing FTP connection")

		ftp.go_dir(ftp_base_folder + folder)
		ftp.up(active_file)
