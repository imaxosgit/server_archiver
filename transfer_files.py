import os
from pathlib import Path
from datetime import date, datetime
import subprocess
import zipfile
import json
import sys


def init_config(config='config.json'):
    try:
        with open(config, 'r', encoding='utf-8') as cfg:
            data = json.loads(cfg.read())
            return data
    except OSError:
        print("Could not open config file:", config)
        sys.exit(1)


def init_logs(data):
    cur_date = date.today().strftime("%Y/%m/%d")
    try:
        Path(data['stdout_log_address'] + cur_date).mkdir(parents=True, exist_ok=True)
        Path(data['stderr_log_address'] + cur_date).mkdir(parents=True, exist_ok=True)
    except BaseException as e:
        print("Couldn't make log directories", type(e))
        sys.exit(1)

    try:
        out_log_path = data['stdout_log_address'] + cur_date + '/output.txt'
        err_log_path = data['stderr_log_address'] + cur_date + '/errors.txt'
        with open(out_log_path, 'a', encoding='utf-8') as out_log, \
                open(err_log_path, 'a', encoding='utf-8') as err_log:
            out_log.write("Started on " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
            err_log.write("Started on " + datetime.now().strftime("%Y/%m/%d-%H:%M:%S") + "\n")
            return out_log_path, err_log_path

    except OSError as e:
        print("Couldn't make log files:", e)
        sys.exit(1)


def transfer(file, data, out_log, err_log):
    # zip the file
    with zipfile.ZipFile(data['storage_address'] + file + '.zip', 'w') as zp:
        zp.write(data['storage_address'] + file)
        new_zip = file + '.zip'
    out_log.write("made new zipfile {}".format(new_zip) + datetime.now().strftime("%Y/%m/%d-%H:%M:%S") + "\n")

    connect_args = ['ssh', "{}@{}".format(data['remote_user'], data['remote_host_address'])]
    mkdir_args = ["mkdir -p " + data['destination_address'] + new_zip[:new_zip.rfind('/')]]
    copy_args = ["scp", data['storage_address'] + new_zip,
                 "{}@{}:{}".format(data['remote_user'], data['remote_host_address'],
                                   data['destination_address'] + new_zip)]

    connect_process = subprocess.run(connect_args + mkdir_args, stdout=out_log, stderr=err_log)
    out_log.write(
        "executed commands: {} ".format(connect_process.args) + datetime.now().strftime("%Y/%m/%d-%H:%M:%S") + "\n")
    scp_process = subprocess.run(copy_args, stdout=out_log, stderr=err_log)
    out_log.write(
        "executed commands: {} ".format(scp_process.args) + datetime.now().strftime("%Y/%m/%d-%H:%M:%S") + "\n")

    os.remove(data['storage_address'] + file)
    out_log.write(
        "deleted file:{} ".format(data['storage_address'] + file) + datetime.now().strftime("%Y/%m/%d-%H:%M:%S") + "\n")

    os.remove(data['storage_address'] + new_zip)
    out_log.write(
        "deleted zip:{} ".format(data['storage_address'] + new_zip) + datetime.now().strftime("%Y/%m/%d-%H:%M:%S") + "\n")
