#!/usr/bin/env python

import ConfigParser
import datetime
import logging
import smtplib
from shutil import make_archive
from socket import gethostname
from email.mime.text import MIMEText

__author__ = "Leonardo Cezar, <leonardo.cezar@dataprev.gov.br>"

class Backup:
	"""
	Rotina de Backup reescrita em Python
	"""
	def __init__(self):
		self.section = 'general'
		self.config = ConfigParser.ConfigParser()
		self.config.readfp(open('backup-udsl.cfg'))
		logging.basicConfig(format="%(levelname)s: %(message)s",filename=self.config.get(self.section,'file_log'),level=logging.DEBUG)

	def _build_mail_list(self):
		domain = self.config.get(self.section,'default_domain')
		users = self.config.get(self.section,'notify_users').split(',')
		user = map(lambda k:( k.strip() + '@' + domain),users)

		return ','.join(user)

	def send_mail(self, subject, body):
		header = MIMEText(body)
		header['Subject'] = "%s %s" % (gethostname(), subject)
		header['From'] = 'sysadmin'
		header['To'] = self._build_mail_list()

		s = smtplib.SMTP('smtp-expresso')
		s.sendmail('backup@dataprev', self._build_mail_list(), header.as_string())

	def copy_data(self, target, source):
		logging.info('Compressing target %s ' % target)
		file_name = target
		root_dir = self.config.get(self.section,'backup_dir')
		
		try:
			make_archive(target,'gztar',source)
		except OSError as (no,str):
			logging.critical(str, \
				self.config.get('general','backup_dir'))
			print str
			

	def run():
		pass

	def shrink(self):
		pass

# Plugins are derivated classes that implements specific backup behavior.
# They need only provides the exec abstract method of superclass. if you're
# writing a new plugin you probably are going to known the better way to make
# backups in command line either using API approach or command line utilities.
class PostgreSQL(Backup):
	def _exec(self):
		dump_file = 'dump.dmp'
		databases = self.config.get('PostgreSQL', 'database')
		if databases == 'all':
			cmd = 'pg_dumpall'
		
		self.copy_data(self.config.get('general','backup_dir')+'pgsql',dump_file)
	def run(self):
		self._exec()

class Svn(Backup):
	pass

class Trac(Backup):
	pass

class UserDir(Backup):
	pass

class Git(Backup):
	pass

class ConfFiles(Backup):
	pass

if __name__ == "__main__":
	full_backup = [PostgreSQL, Svn, Trac, UserDir]
	b = PostgreSQL()
	b.run()
#	print b.send_mail('teste de assunto','teste backup')
