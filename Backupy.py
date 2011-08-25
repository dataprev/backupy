#!/usr/bin/env python

import ConfigParser
import datetime
import logging
import smtplib
import os
import subprocess
from shutil import make_archive
from socket import gethostname
from email.mime.text import MIMEText

__author__ = "Leonardo Cezar, <leonardo.cezar@dataprev.gov.br>"
__all__    = ['PostgreSQL', 'Svn']
CFG = 'backup.cfg'
# WTF!!! no inspiration... 
PG_DIR = '/tmp/postgres.bkp.tmp'

class Backupy:
	"""
	Rotina de Backup reescrita em Python
	"""
	def __init__(self):
		self.section = 'general'
		self.config = ConfigParser.ConfigParser()
		self.config.readfp(open(CFG))

		format = "%(asctime)s %(message)s"
		logging.basicConfig(format=format, \
				filename=self.config.get(self.section,'file_log'),level=logging.DEBUG)

	@property
	def users_mail(self):
		domain = self.config.get(self.section,'default_domain')
		users = self.config.get(self.section,'notify_users').split(',')
		address = map(lambda k:( k.strip() + '@' + domain),users)

		return ','.join(address)

	def send_mail(self, subject, body):
		header = MIMEText(body)
		header['Subject'] = "%s %s" % (gethostname(), subject)
		header['From'] = 'sysadmin'
		header['To'] = self.users_mail

		s = smtplib.SMTP('smtp-expresso')
		s.sendmail('backup@dataprev', self.users_mail, header.as_string())

	def copy_data(self, filename, source):
		logging.info('Compressing target %s ' % source)
		root_dir = self.config.get(self.section,'backup_dir')
		
		try:
			make_archive(filename,'gztar',source)
		except OSError as e:
			logging.critical(e.strerror)
			print e.strerror + ' ' + source
			

	def run():
		pass

	def shrink(self):
		pass

# Plugins are derivated classes that implements specific backup behavior.
# They need only provides the exec abstract method of superclass. if you're
# writing a new plugin you probably are going to known the better way to make
# backups in command line either using API approach or command line utilities.
class PostgreSQL(Backupy):
	def _exec(self):
		dump_dir = 'db-backup'

		databases = self.config.get('PostgreSQL', 'database')
		file_output = 'postgres.dmp'
		options = ['-U postgres','-p5432','-Fc','-f'+file_output]

		if databases == 'all':
			cmd = ['pg_dumpall']+options
		else:
			cmd = ['pg_dump',self.config.get('PostgreSQL','database')]+options
		
		try:
			cmd_exec = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError, e:
			logging.info(e.output)
			return

		try:
			os.makedirs(PG_DIR)
		except OSError:
			self.copy_data('postgres',dump_dir)
		except:
			print 'unable to create pgbackup dir'
		
	#	self.config.get('general','backup_dir')+'pgsql'
	def run(self):
		self._exec()

class Svn(Backupy):
	def run(self):
		print self.__class__

	pass

class Trac(Backupy):
	pass

class UserDir(Backupy):
	pass

class Git(Backupy):
	pass

class ConfFiles(Backupy):
	pass

def _build_repr(cls):
	i = eval(cls)()
	i.run()

if __name__ == "__main__":
	cfg = ConfigParser.ConfigParser()
	cfg.readfp(open(CFG))	
	backup_items = cfg.get('general','items').split(',')

	map(lambda b: _build_repr(b.strip()), backup_items)


#	b = PostgreSQL()
#	b.run()
#	print b.send_mail('teste de assunto','teste backup')
