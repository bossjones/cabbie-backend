# scripts/register_cu_event_code.py

import xlrd
import math

from cabbie.apps.event.models import CuEventCode

def run():

    # already registered
    codes = CuEventCode.objects.values('code')
    already = [dic['code'] for dic in codes.all()]

    cu_file = xlrd.open_workbook("bktaxi_cu_event_code_20151117_2.xlsx")
    sh = cu_file.sheet_by_index(0)

    new = 0
    old = 0

    for rx in range(sh.nrows):
        if rx == 0:
            continue

        value = sh.row(rx)[5].value

        if isinstance(value, float):
            value = '%.0f' % value

        if value in already:
            old += 1
            print 'skip, {0} is already registered'.format(value)
            continue

        new += 1
        print rx, value

        #CuEventCode.objects.create(code=value)

    print 'Total: {0}, New: {1}, Already: {2}'.format(new+old, new, old)
