# scripts/register_cu_event_code.py

import xlrd
import math

from cabbie.apps.event.models import CuEventCode

def run():

    cu_file = xlrd.open_workbook("bktaxi_cu_event_code_20151116.xlsx")
    sh = cu_file.sheet_by_index(0)

    for rx in range(sh.nrows):
        if rx == 0:
            continue

        value = sh.row(rx)[5].value

        if isinstance(value, float):
            value = '%.0f' % value

        print rx, value

        #CuEventCode.objects.create(code=value)
