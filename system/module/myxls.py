import xlwt
import xlrd
from xlrd.timemachine import xrange


def read_xls(name_file, start_rows=0):
    book = xlrd.open_workbook(name_file, on_demand=True)
    sheet = book.sheet_by_index(0)
    data = [[c.value for c in sheet.row(i)] for i in xrange(start_rows, sheet.nrows)]
    book.release_resources()
    del book
    return data


def write_xls(name_file, list):
    font0 = xlwt.Font()
    font0.name = 'Arial'
    font0.bold = True
    style0 = xlwt.XFStyle()
    style0.font = font0
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Result')
    for i, l in enumerate(list):
        for j, el in enumerate(l):
            ws.write(i, j, el, xlwt.XFStyle() if i else style0)
    wb.save(name_file)
