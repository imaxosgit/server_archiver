import threading
import os
import shutil
import time
from datetime import datetime

from transfer_files import transfer, init_config, init_logs

if __name__ == "__main__":

    data = init_config()
    out_log, err_log = init_logs(data)

    def gen_file_list(p):
        for root, dirs, files in os.walk(p):
            for name in files:
                extension = os.path.splitext(name)[-1].lower()
                if extension == '.mp3' or extension == '.wav':
                    # check if avaible space is below 10% or file is outdated
                    file_age = os.path.getmtime(os.path.join(root, name))
                    total, used, free = shutil.disk_usage("/")
                    if free/total < 0.1 or (time.time() - file_age > (90 * 24 * 60 * 60)):
                        yield os.path.join(root[len(data['storage_address']):], name)


    with open(out_log, 'a', encoding='utf-8') as out, open(err_log, 'a', encoding='utf-8') as err:

        try:
            threads = []

            fls = gen_file_list(data['storage_address'])

            for f in fls:
                t = threading.Thread(target=transfer, args=[f, data, out, err])
                threads.append(t)
                t.start()

            for i in threads:
                i.join()

        except BaseException as e:
            err.write("Unexpected exception occured: {}".format(e))

        out.write('Ended on ' + datetime.now().strftime("%Y/%m/%d-%H:%M:%S") + "\n")
