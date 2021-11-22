# -*- coding: utf-8 -*-
# @Time    : 2021/11/22 10:34
# @Author  : HundredW
# @Github  : https://github.com/HundredW
# @Email   : han.wang@stu.pku.edu.cn
# @File    : F3E_SCIHUB.py
# @Des     : Find and download full text for endnote library by DOIs via sci-hub;
#            JUST FOR THOES Paper Reference THAT DO NOT HAVE ANY Attachment
# Ackonwledgement: Some scripts for download file is
#                  from https://github.com/stormsuresh92/Sci-Hub_Automation/blob/main/SciHub_PDF_Automate_By_DOIs.py

import os
import sqlite3
import re
import time

from bs4 import BeautifulSoup

import requests


def get_doi_numbers(lib_file_path=""):
    lib_name = ""
    dir_name = ""
    if lib_file_path != "":
        lib_name = os.path.basename(lib_file_path).replace(".enl", "")
        dir_name = os.path.dirname(lib_file_path)
    lib_db_file = os.path.join(dir_name, lib_name + ".Data", "sdb", "sdb.eni")
    print(lib_db_file)
    conn = sqlite3.connect(lib_db_file)
    c = conn.cursor()
    cursor = c.execute(
        "SELECT electronic_resource_number,fulltext_downloads " +
        "FROM refs WHERE (fulltext_downloads is NULL OR TRIM(fulltext_downloads)='')"
        " and (TRIM(electronic_resource_number)!='');")
    doi_error = []
    doi = []
    for row in cursor:
        doi_record = row[0]
        reg = """(10[.][0-9]{4,}[^\s"/<>]*/[^\s"<>]+)$"""
        obj = re.search(reg, str(doi_record))
        if not (obj):
            doi_error.append(doi_record)
        else:
            doi.append(obj.group())
    return doi, doi_error


def get_pdf_from_sci_hub(sci_hub_bl="https://www.sci-hub.ru", dois=[]):
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'Connection': 'keep-alive',
        'Keep-Alive': 'timeout=60'
    }

    cur_dir = os.getcwd()
    pdf = cur_dir + '/Downloaded PDFs'
    if not os.path.exists(pdf):
        os.mkdir(pdf)

    print('******************************')
    print('STARTING TO WRITE PDF FILES...')
    for doi in dois:
        doiname = doi.replace('/', '-')
        print(doiname)
        try:
            payload = {
                'sci-hub-plugin-check': '',
                'request': str(doi.strip())
            }
            base_url = sci_hub_bl
            r = requests.post(base_url, headers=header, data=payload)
            soup = BeautifulSoup(r.content, 'html.parser')
            cont = soup.find(id='pdf').get('src').replace('#navpanes=0&view=FitH', '')
            if not cont.startswith('https:'):
                pdfurl = 'https:' + str(cont)
            else:
                pdfurl = cont

            res = requests.get(pdfurl, stream=True)
            with open(pdf + '/' + doiname.strip() + '.pdf', 'wb') as f:
                for chunk in res.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except:
            NoPDF = open('PDF_NOT_FOUND.txt', 'a')
            NoPDF.write(doi.strip() + '\n')
        time.sleep(1)


if __name__ == "__main__":
    sci_hub_base_url = "https://www.sci-hub.ru"
    while True:
        lib_path = input("Please input the path str your endnote library file:\n")
        if os.path.isfile(lib_path):
            dois = get_doi_numbers(lib_path)[0]
            if len(dois) > 0:
                print(str(len(dois)) + " DOIs need to to be downloaded.")
                get_pdf_from_sci_hub(sci_hub_base_url, dois)
            else:
                print("No doi needs to be downloaded")
        else:
            print("Invalid file path!")
