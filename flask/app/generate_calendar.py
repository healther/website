# -*- coding: UTF-8 -*-

import ics
import xlrd
import os
import datetime
import time
import pytz

# ensure correct time zone
os.environ['TZ'] = 'Europe/Berlin'
time.tzset()

# patch py3.8 incompatibility
xlrd.book.time.clock = xlrd.book.time.process_time


def create_event(date, title, headers, dienstday):
    unwanted_headers = ['Date']
    for uh in unwanted_headers:
        dienstday.pop(uh)
    local_headers = [h for h in headers if h not in unwanted_headers]
    description = ''
    for h in local_headers:
        description += '{:s}\t{}\n'.format(h+': ', dienstday[h])
    date = date.replace(hour=10)
    localtz = pytz.timezone('Europe/Berlin')
    date = localtz.localize(date)

    e = ics.icalendar.Event(name=title, begin=date, duration=datetime.timedelta(hours=23),
                            created=datetime.datetime.now(), description=description)
    return e

def get_datetime(year, date):
    day, month, _ = date.split('.')
    d = datetime.datetime(year=int(year), month=int(month), day=int(day))
    return d

def extract_from_xlrd(inputfilename, doctorname):
    wb = xlrd.open_workbook(inputfilename)
    sheet = wb.sheets()[0]

    # The header of the Dienst table (which contains the names) is in the 4th row
    # The first two columns are weekday and date, we want to keep the date.
    # The rest of the columns are the different Dienstgruppen (header) and the
    # doctors doing the Dienst (table body)
    # last row may contain a vorläufig marker
    rowoffset = 4
    columnoffset = 1

    # First get the year and whether it is december
    year = sheet.cell_value(1, 3)
    # December is a special case, it also includes part of january...
    endofyear = False
    # if we have december, the "Jahr" field will be 20XX/20${XX+1}$
    # which is not a valid date entry and hence the field value will
    # be of type str
    if type(year) in [str]:
        year = int(year.split('/')[0])
        endofyear = True

    # get the header entries, the date column does not have a usable header
    headers = [c.value for c in sheet.row(rowoffset-1)[columnoffset:]]
    headers[0] = 'Date'

    cal = ics.icalendar.Calendar()
    for rowid in range(sheet.nrows)[rowoffset:]:
        dienstday = {key: cell.value for key, cell in zip(headers, sheet.row(rowid)[columnoffset:])}
        # clean unwanted rows
        datestr = dienstday['Date']
        # check for complete name
        if doctorname in dienstday.values():
            diensttype = list(dienstday.keys())[list(dienstday.values()).index(doctorname)]
            if type(datestr) is float:
                datetuple = xlrd.xldate_as_tuple(datestr, wb.datemode)
                date = datetime.datetime(*datetuple)
            else:
                if endofyear:
                    date = get_datetime(year+1, datestr)
                else:
                    date = get_datetime(year, datestr)
            cal.events.add(create_event(date, title=diensttype, headers=headers, dienstday=dienstday))

    return cal

def main(inputfilename, outputpath, doctorname):
    if inputfilename.endswith('.xlrd') or inputfilename.endswith('.xls'):
        cal = extract_from_xlrd(inputfilename, doctorname)
    elif inputfilename.endswith('.pdf'):
        data = extract_from_pdf(inputfilename, doctorname)
        cal = transform_into_calendar(data, doctorname)
    else:
        raise ValueError('Wrong format, can only deal with .pdf and .xlrd')

    filename = 'dienste_{}.ics'.format(doctorname)
    with open(os.path.join(outputpath, filename), 'w') as f:
        f.writelines(cal)
    return filename


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Parses the schedule of the clinic and dumps an ics version of all Dienste for a given doctor.")
    parser.add_argument("inputfilename", help="Schedule xls file")
    parser.add_argument("doctorname", help="Name for which the event file should be created")

    args = parser.parse_args()

    argdict = vars(args)
    argdict['outputpath'] = '.'
    main(**argdict)
