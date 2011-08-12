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

	def copy_data(self, source, target):
		logging.info('Compressing target %s ' % target)
		file_name = target
		root_dir = self.config.get(self.section,'backup_dir')+source
		make_archive(file_name,'gztar',root_dir)

	def shrink(self):
		pass

if __name__ == "__main__":
	b = Backup()
	print b.send_mail('teste de assunto','teste backup')
