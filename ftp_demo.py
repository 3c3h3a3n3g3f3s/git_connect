import datetime
import ftplib
import json
import math
import os
import pandas as pd
SBM_FILE_PREFIX=""
STORE_FILE_PREFIX=""

ftp_host=""
ftp_port=""
FTP_USER=""
FTP_PASS=""
LOCAL_DATA_DIR=""
FTP_REMOTE_DIR=""
def get_filename(prefix):
    now = datetime.datetime.now()
    return prefix + now.strftime("%Y%m%d") + '.csv'


def get_ftp_conn():
    ftp = ftplib.FTP()
    ftp.connect(ftp_host, ftp_port)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp


def get_data(filename):
    ftp = get_ftp_conn()

    with open(LOCAL_DATA_DIR + filename, 'wb') as fp:
        try:
            ftp.retrbinary('RETR ' + FTP_REMOTE_DIR + filename, fp.write)
        except Exception:
            #log.exception('Error downloading file: %s', filename)
            ftp.close()
            return
    df = pd.read_csv(LOCAL_DATA_DIR + filename, header=None, sep=',',
                     low_memory=False)
    data_dict={}
    df.fillna(0)
    data=df.values.tolist()[1:]
    columns=df.values.tolist()[0]
    df_data=pd.DataFrame(data,columns=columns)
    df_data['FAMOUNT_MA']=df_data['FAMOUNT_MA'].astype('float64')
    data_dict['positive_payment']=math.ceil(df_data[df_data['FAMOUNT_MA']>0]['FAMOUNT_MA'].sum())
    data_dict['negative_amount']=math.ceil(df_data[df_data['FAMOUNT_MA']<0]['FAMOUNT_MA'].sum())
    data_dict['check_sum']=len(data)
    if 'SaleDetail_OLD_' not in filename:
        data_dict["member_order"]=len(df_data[df_data['FMOBILENUMBER']!=0].drop_duplicates(subset=['FMOBILENUMBER']))-1
    done_filename = filename + '.done'

    with open(LOCAL_DATA_DIR + done_filename, 'w') as f:
        json.dump(data_dict, f)

    with open(LOCAL_DATA_DIR + done_filename, 'rb') as f:
        ftp.storbinary('STOR ' + FTP_REMOTE_DIR + done_filename, f)

    ftp.close()
    os.remove(LOCAL_DATA_DIR + filename)
    os.remove(LOCAL_DATA_DIR + done_filename)


def run():
    for prefix in [SBM_FILE_PREFIX, STORE_FILE_PREFIX]:
        filename = get_filename(prefix)
        get_data(filename)