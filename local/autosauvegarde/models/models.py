# -*- coding: utf-8 -*-

from odoo import models, fields, api
import glob
import logging
import os
import tarfile
from datetime import datetime, timedelta
from logging import FileHandler
from ftplib import FTP_TLS
from threading import Thread


def supplogs(lg):
    d = datetime.today() - timedelta(days=7)
    lg.info(str(d.strftime("%Y%m%d")) + ' is the limit of days')
    for n in glob.glob('logs/*'):
        if (n.split("-")[0] < str(d.strftime("%Y%m%d"))):
            try:
                lg.info(n + ' removed')
                os.remove('logs/' + n)
            except(FileNotFoundError):
                pass


def filestoring(lg,flt):
    if os.path.isdir(flt):
        tf = tarfile.open("temp/filestore.tar.gz", mode="w:gz", compresslevel=9)
        for file in glob.glob(flt + "/*"):
            lg.info(file + ' compressed')
            tf.add(file)

        tf.close()
    else:
        lg.error('No Filestore !')


def dbdumping(lg, db):
    lg.info('Database ' + db + ' detected')
    try:
        os.system('pg_dump --format=t ' + db + ' | gzip -9 > temp/db_' + db + '.tar.gz')
        lg.info('Database saved')
    except():
        lg.error('pg_dump missed')


def isdir(ftp, name):
    try:
        ftp.cwd(name)
        ftp.cwd('/')
        return True
    except:
        return False


def remove_ftp_dir(ftp, path):
    for (name, properties) in ftp.mlsd(path=path):
        if name in ['.', '..']:
            continue
        elif properties['type'] == 'file':
            ftp.delete(f"{path}/{name}")
        elif properties['type'] == 'dir':
            remove_ftp_dir(ftp, f"{path}/{name}")
    ftp.rmd(path)


def multiple_transfer(lg, ftp, db, sauvegarde):
    # try:
    ftp.connect(str(sauvegarde.host))
    ftp.sendcmd('USER ' + str(sauvegarde.login))
    ftp.sendcmd('PASS ' + str(sauvegarde.pwd))

    lg.info('Connection to ' + str(sauvegarde.name) + ' performed')

    init_path = str(sauvegarde.ftp_path)
    lg.info('Path is ' + init_path)
    final_path = ''

    for n in init_path.split('/'):
        if final_path == '':
            final_path = n
        else:
            final_path = final_path + '/' + n
        if not isdir(ftp, final_path):
            ftp.mkd(final_path)
            lg.info(final_path + ' Created')

    if init_path[-1] != '/':
        init_path = init_path + '/'

    d = datetime.today() - timedelta(days=sauvegarde.nb_days_save)

    lg.info(str(d.strftime("%Y%m%d")) + ' is the limit of days')
    files = ftp.nlst(init_path)
    for n in files:
        if n in ['.', '..']:
            continue
        elif n < str(d.strftime("%Y%m%d")):
            lg.info('Removing folder ' + n)
            remove_ftp_dir(ftp, init_path + n)
            lg.info(n + ' Folder removed')

    final_path = init_path + str(datetime.now().strftime("%Y%m%d-%H%M%S"))
    lg.info('Création de ' + final_path)
    ftp.mkd(final_path)

    flst = open('temp/filestore.tar.gz', 'rb')
    datab = open('temp/db_' + db + '.tar.gz', 'rb')
    lg.info('Transfer of ' + db)
    ftp.storbinary('STOR ' + final_path + '/db_' + db + '.tar.gz', datab)
    lg.info('DataBase Transferred')
    lg.info('Transfer of filestore')
    ftp.storbinary('STOR ' + final_path + '/filestore.tar.gz', flst)
    lg.info('Filestore Transferred')

    flst.close()
    datab.close()
    lg.info('Files Closed')
    ftp.close()
    lg.info('Success !!!')
    # except:
    # lg.error('Connection failed to ' + str(sauvegarde.name))


class Sauvegarde(models.Model):
    _name = "autosauvegarde.save"
    _description = 'Odoo\'s Save'

    name = fields.Char('FTP Server Name', required=True)
    active = fields.Boolean('Active')
    host = fields.Char('Host', required=True)
    login = fields.Char('Login', required=True)
    pwd = fields.Char('Password', required=True)
    nb_days_save = fields.Integer('BackUp Expiring days', default=7)
    nb_days_log = fields.Integer('Logs Expiring days', default=7)
    ftp_path = fields.Char('FTP Folder', default='')
    filestore_path = fields.Char('Filestore Folder', default='filestore')

    @api.model
    def sauvegarde(self):

        lg = logging.getLogger()
        lg.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s;')

        file_handler = FileHandler('logs/' + datetime.now().strftime("%Y%m%d-%H-%M-%S") + '.log', 'a')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        lg.addHandler(file_handler)

        lg.info('Start Log')

        if not os.path.isdir('temp'):
            os.mkdir('temp')
            lg.info('Temp folder created')

        splogs = Thread(None, supplogs(lg))
        flt = self.search([])[0].filestore_path
        flstr = Thread(None, filestoring(lg,flt))
        db = str(self._cr.dbname)
        dbdp = Thread(None, dbdumping(lg, db))


        splogs.start()
        flstr.start()
        dbdp.start()

        flstr.join()
        dbdp.join()
        splogs.join()
        lg.info('Start of the transfer')
        ftp = FTP_TLS()
        ftp.set_debuglevel(2)

        sauvegardes = self.search([])
        for sauvegarde in sauvegardes:
            if sauvegarde.active:
                multiple_transfer(lg, ftp, db, sauvegarde)
