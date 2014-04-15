import csv
import yaml
import datetime

file = open('termdates.csv','r')
reader = csv.reader(file)
counter = 1
term_dates = []
for row in reader:
    year = int(row[0].split('–')[0])
    m_start_month = 10
    if int(row[2]) >= 15:
        m_end_month = 11
    else:
        m_end_month = 12
    l_start_month = 1
    l_end_month = 3
    e_start_month = 4
    e_end_month = 6
    mt_start = datetime.date(year=year, month=m_start_month, day=int(row[1]))
    cb_start = datetime.date(year=year, month=m_end_month, day=int(row[2]))
    lt_start = datetime.date(year=year, month=l_start_month, day=int(row[3]))
    eb_start = datetime.date(year=year, month=l_end_month, day=int(row[4]))
    et_start = datetime.date(year=year, month=e_start_month, day=int(row[5]))
    sb_start = datetime.date(year=year, month=e_end_month, day=int(row[6]))
    mt_start = datetime.date.fromordinal(mt_start.toordinal() - mt_start.weekday())
    lt_start = datetime.date.fromordinal(lt_start.toordinal() - lt_start.weekday())
    et_start = datetime.date.fromordinal(et_start.toordinal() - et_start.weekday())
    cb_start = datetime.date.fromordinal(cb_start.toordinal() - cb_start.weekday() + 7)
    eb_start = datetime.date.fromordinal(eb_start.toordinal() - eb_start.weekday() + 7)
    sb_start = datetime.date.fromordinal(sb_start.toordinal() - sb_start.weekday() + 7)
    term_dates.append({'model':'drama.TermDate', 'pk':counter, 'fields':{'term':'MT', 'year':year, 'start':mt_start}})
    counter += 1
    term_dates.append({'model':'drama.TermDate', 'pk':counter, 'fields':{'term':'CB', 'year':year, 'start':cb_start}})
    counter += 1
    term_dates.append({'model':'drama.TermDate', 'pk':counter, 'fields':{'term':'LT', 'year':year, 'start':lt_start}})
    counter += 1
    term_dates.append({'model':'drama.TermDate', 'pk':counter, 'fields':{'term':'EB', 'year':year, 'start':eb_start}})
    counter += 1
    term_dates.append({'model':'drama.TermDate', 'pk':counter, 'fields':{'term':'ET', 'year':year, 'start':et_start}})
    counter += 1
    term_dates.append({'model':'drama.TermDate', 'pk':counter, 'fields':{'term':'SB', 'year':year, 'start':sb_start}})
    counter += 1
print(yaml.dump(term_dates, default_flow_style=False))
    
