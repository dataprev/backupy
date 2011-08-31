#!/usr/bin/env python

import ConfigParser
import datetime
import logging
import smtplib
import os
import subprocess
from shutil import make_archive, move
from socket import gethostname
from email.mime.text import MIMEText

__author__ = "Leonardo Cezar, <leonardo.cezar@dataprev.gov.br>"
__all__    = ['PostgreSQL', 'Svn']
CFG = 'backup.cfg'
# WTF!!! no inspiration... 
STAGE_DIR = '/tmp/stage_bkp_dir/'

class Backupy:
    """
    Rotina de Backup reescrita em Python
    """
    def __init__(self):
        self.section = 'general'
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(CFG))
        self.create_stagedir()

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

    def copy_file(self,src,dst):
        try:
            os.copy(src, dst)
        except IOError, e:
            logging.error(e)

    def __enter__(self):
        # perhaps we should using this placeholder as a initializer? 
        pass
    def __exit__(self,type,value,traceback):
        backup_dir = self.config.get(self.section,'backup_dir')
        item_backup = str(self.__class__).split('.')[1].lower()
        server_name = gethostname().split('.')[0]
    
        filename = "%s_%s_%s" % (server_name,item_backup, \
                str(datetime.datetime.now().isoformat()).replace(":-",""),)
        try:
            make_archive(filename,'gztar',STAGE_DIR)
        except OSError as e:
            logging.critical(e.strerror)
            print e.strerror + ' ' + source

    def create_stagedir(self):
        try:
            if not os.path.exists(STAGE_DIR):
                os.makedirs(STAGE_DIR)
        except OSError, e:
            logging.critical(e)
            exit("Unable go ahead without a stage area")
        except:
            print 'unable to create pgbackup dir'
    

    def run():
        pass

    def shrink(self):
        pass

# Plugins are derivated classes that implements specific backup behavior.
# They need only provides the exec abstract method of superclass. if you're
# writing a new plugin you probably are going to known the better way to make
# backups in command line either using API approach or command line utilities.
class PostgreSQL(Backupy):
    """
    we trust there is a .pgpass file within your $HOME with this format:
    localhost:5432:*:postgres:postgres
    localhost:5433:*:postgres:postgres
    
    This is the only way to get pg_dump working securely
    """
    def _exec(self):
        dump_dir = 'db-backup'

        databases = self.config.get('PostgreSQL', 'database')
        file_output = STAGE_DIR+'postgres.tar.gz'
        # file to be send to storage area
        self._file = file_output
        options = ['-Fc','-f'+file_output]

        if databases == 'all':
            cmd = ['pg_dumpall']+options
        else:
            cmd = ['pg_dump',self.config.get('PostgreSQL','database')]+options
        
        try:
            cmd_exec = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            logging.critical(e.output)
            return

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
    with eval(cls)() as i:
        if isinstance(i, Backupy):
            i.run()

if __name__ == "__main__":
    cfg = ConfigParser.ConfigParser()
    cfg.readfp(open(CFG))   
    backup_items = cfg.get('general','items').split(',')

    map(lambda b: _build_repr(b.strip()), backup_items)


#   b = PostgreSQL()
#   b.run()
#   print b.send_mail('teste de assunto','teste backup')
