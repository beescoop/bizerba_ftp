#! python3
# coding: utf-8


"""Download files needed by the Bizerba scales from an FTP server.

Autor:
    Rémy Taymans <remytaymans@gmail.com>
Current Maintainer:
    Rémy Taymans <remytaymans@gmail.com>
Creation: 10 oct 2017
Last change: 11 oct 2017

Usage:
    Write in the configuration file:
        - ftp address
        - ftp user
        - ftp password
        - ftp directory for csv
        - ftp directory for old csv
        - ftp directory for image
        - local folder for csv
        - local folder for image
        - location of the log file
    Then run this script.
"""


from ftplib import FTP
import logging
import os

import configparser


__author__ = "Rémy Taymans"
__copyright__ = "Copyright 2017, Rémy Taymans"
__credits__ = ["Rémy Taymans"]
__license__ = "GPLv3"
__version__ = "0.2"
__maintainer__ = "Rémy Taymans"
__email__ = "remytaymans@gmail.com"
__status__ = "Development"


CONFIG_FILENAME = "bizerba.conf"
LOG_FILENAME = "bizerba.log"


def main():
    """Program start here"""

    # Read config file
    config = get_config()

    # Open config file
    try:
        logfilename = config.get('log', 'filename').strip('"')
    except configparser.Error:
        logfilename = LOG_FILENAME
    logging.basicConfig(
        filename=logfilename,
        format='%(asctime)s - %(levelname)s : %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logging.info("Check the config file")

    # Check config file
    if not check_config(config):
        logging.critical("The config file is not properly writed")
        exit(1)

    logging.info("Config file check passed successfully")

    logging.info("Starts running script")

    # Connect to FTP
    logging.info('Open connection with FTP server')
    ftp = FTP(config['ftp'].get('address').strip('"'))
    ftp.login(
        user=config['ftp'].get('user').strip('"'),
        passwd=config['ftp'].get('password').strip('"')
    )

    # Set encoding
    ftp.encoding = "cp1252"

    # Get images frist than files
    get_image_files(ftp, config)
    get_csv_files(ftp, config)

    try:
        ftp.quit()
        logging.info('Quit connection')
    except Exception:
        ftp.close()
        logging.info('Close connection')


def get_config(config_filename=CONFIG_FILENAME):
    """Return the config file as an object"""
    config = configparser.ConfigParser()
    config.read(config_filename)
    return config


def check_config(config):
    """Check that the config file have all the required field"""
    try:
        config.get('ftp', 'address')
        config.get('ftp', 'user')
        config.get('ftp', 'password')
        config.get('ftp', 'csv_dir')
        config.get('ftp', 'backup_csv_dir')
        config.get('ftp', 'image_dir')
    except configparser.Error as err:
        logging.error(err)
        return False

    try:
        config.get('local', 'csv_dir')
        config.get('local', 'image_dir')
    except configparser.Error as err:
        logging.error(err)
        return False

    try:
        config.get('log', 'filename')
    except configparser.Error as err:
        logging.error(err)
        return False

    return True


def remove_hidden_files(files):
    """Remove hidden file form the list given in args"""
    new_files = []
    for f in files:
        if not f.startswith('.'):
            new_files.append(f)
    return new_files


def keep_only_csv(files):
    """Remove all the files that are not csv in the list given in
    args"""
    new_files = []
    for f in files:
        f_low = f.lower()
        if f_low.endswith('.csv'):
            new_files.append(f)
    return new_files


def get_csv_files(ftp, config, move_csv_to_backup=True):
    """Download the csv files from the right directory on the ftp server
    into the right local directory. If move_csv_to_backup is True, the
    csv file on the ftp are moved from their original place to the
    backup dir.
    """
    # Change local working directory to CSV import directory
    os.chdir(config['local'].get('csv_dir').strip('"'))
    logging.info('Working in %s directory', os.getcwd())

    # Get CSV files
    ftp.cwd(config['ftp'].get('csv_dir').strip('"'))
    files = ftp.nlst()
    files = remove_hidden_files(files)
    files = keep_only_csv(files)

    for f in files:
        logging.info('Writing %s', f)
        get_text_file_from_ftp(ftp, f)
        if move_csv_to_backup:
            logging.info(
                'Move %s to %s/%s',
                f,
                config['ftp'].get('backup_csv_dir').strip('"'),
                f
            )
            ftp.rename(
                f,
                '%s/%s' % (
                    config['ftp'].get('backup_csv_dir').strip('"'),
                    f
                )
            )


def get_image_files(ftp, config):
    """Download the image files from the right directory on the ftp
    server into the right local dirctory.
    """
    # Change local working directory to image import directory
    os.chdir(config['local'].get('image_dir').strip('"'))
    logging.info('Working in %s directory', os.getcwd())

    # Get images
    ftp.cwd(config['ftp'].get('image_dir').strip('"'))
    files = ftp.nlst()
    files = remove_hidden_files(files)

    for f in files:
        logging.info('Writing %s', f)
        get_binary_file_from_ftp(ftp, f)


def get_text_file_from_ftp(ftp, f):
    """Download a text file from an existing FTP connection.
    The transfer is in cp1252.
    """
    with open(f, 'w', encoding="cp1252") as local_file:
        ftp.retrlines(
            'RETR %s' % f,
            lambda s, w=local_file.write: w(s+'\n')
        )


def get_binary_file_from_ftp(ftp, f):
    """Download a file from an existing FTP connection.
    The transfer is done in binary mode.
    """
    with open(f, 'wb') as local_file:
        ftp.retrbinary('RETR %s' % f, local_file.write)


if __name__ == "__main__":
    main()
