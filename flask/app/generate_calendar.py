import ics
import xlrd
import datetime


def create_event(date, diensttype):
    e = ics.icalendar.Event(name=diensttype, begin=date, duration=datetime.timedelta(hours=26),
                            created=datetime.datetime.now())
    return e

def get_datetime(year, date):
    day, month, _ = date.split('.')
    d = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=7)
    return d

def main(filename, doctorname):
    wb = xlrd.open_workbook(filename)
    sheet = wb.sheets()[0]

    # The header of the Dienst table (which contains the names) is in the 4th row
    # The first two columns are weekday and date
    rowoffset = 4
    columnoffset = 2

    # First get the dates (which are in format DD.MM) and the year
    dates_in_month = sheet.col_values(1)[rowoffset:]
    year = sheet.cell_value(1, 3)
    # December is a special case, it also includes part of january...
    endofyear = False
    # if we have december, the "Monat" field will be Dezember/Januar
    # which is not a valid date entry and hence the field value will
    # be of type str
    if type(year) in [str]:
        year = int(year.split('/')[0])
        endofyear = True

    # Then deal with the different dienst types
    dienst_types = sheet.row_values(3)[columnoffset:]
    dienste = {}
    for i, dienstname in enumerate(dienst_types):
        dienste[dienstname] = sheet.col_values(columnoffset+i)[rowoffset:]

    cal = ics.icalendar.Calendar()
    for dienstname, dienstlist in dienste.items():
        for date_in_month, name in zip(dates_in_month, dienstlist):
            if name==doctorname:
                # if we are in Dezember/Januar we need to distinguish
                # between december (normal) days and january (from next
                # year) days.
                if endofyear and '.01.' in date_in_month:
                    date = get_datetime(year+1, date_in_month)
                else:
                    date = get_datetime(year, date_in_month)
                cal.events.add(create_event(date, diensttype=dienstname))

    filename = 'dienste_{}.ics'.format(doctorname)
    with open('downloads/' + filename, 'w') as f:
        f.writelines(cal)
    return filename


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Parses the schedule of the clinic and dumps an ics version of all Dienste for a given doctor.")
    parser.add_argument("filename", help="Schedule xls file")
    parser.add_argument("doctorname", help="Name for which the event file should be created")

    args = parser.parse_args()

    main(**vars(args))
