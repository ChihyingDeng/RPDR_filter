from datetime import datetime
import collections
import pandas as pd
import os
import sys

def reformat_dates(timestamp_string):
    fmts = ('%m/%d/%Y','%Y/%m/%d','%m/%d/%y','%m-%d-%Y','%Y-%m-%d','%m-%d-%y','%b %d, %Y','%b %d, %Y','%B %d, %Y','%B %d %Y','%b %d,%Y')
    date = None
    for fmt in fmts:
        try:
           date = datetime.strptime(timestamp_string, fmt); break
        except ValueError as err:
           pass
    return date

def convert_timestamp_to_seconds(date):
    epoch = datetime.utcfromtimestamp(0)
    return (date - epoch).total_seconds()

def get_empi_to_date_range(filter_filename, patient, date, include, days_before, days_after):
    empi_to_date_range = collections.defaultdict(list)  # map empi to (seconds_start, seconds_end)

    if include == 'All':
        filter_df = pd.read_csv(filter_filename, usecols=[
                                patient, date])
    else:
        filter_df = pd.read_csv(filter_filename, usecols=[
                                patient, date, include])
    one_day_seconds = 60 * 60 * 24
    for i in range(len(filter_df)):
        empi, procedure_date = filter_df[patient][i], reformat_dates(filter_df[date][i])
        # check if empi and procedure are in correct format
        if (isinstance(empi, str) and not empi.isdigit()) or not procedure_date: 
            return "error"
        elif isinstance(empi, str):
            empi = int(empi)
        procedure_date_seconds = convert_timestamp_to_seconds(procedure_date)
        start_date_seconds = (procedure_date_seconds -
                                days_before * one_day_seconds)
        end_date_seconds = (procedure_date_seconds +
                            days_after * one_day_seconds)
        empi_to_date_range[empi].append({'start':start_date_seconds, 
            'end':end_date_seconds, 
            'include':1 if include == 'All' else int(filter_df[include][i])})

    return empi_to_date_range

def filter_rpdr_file(input_fname, empi_to_date_range, days_before, days_after):
    with open(input_fname, 'r') as file:
        data, header, fields = [], [], []
        for line in file:
            line = line.rstrip()
            if line.strip() == '':
                continue
            if not header:
                if line.count('|') < 8:
                    return "error"
                header = [field.lower().strip()
                            for field in line.split('|')]
                continue
            if not fields and '|' in line:
                fields = [field.lower().strip()
                            for field in line.split('|')]
                fields[-1] = line
                report = []
            elif 'report_end' in line:
                report.append(line)
                fields[-1] += '\n'.join(report)

                column_name_to_key = {column_name: key for (column_name, key) in zip(header, fields)}
                empi = int(column_name_to_key.get('empi'))    
                # ignore the patient not in the filter list
                if empi in empi_to_date_range:
                    note_date = (column_name_to_key.get('report_date_time') or
                                column_name_to_key.get('lmrnote_date'))
                    if not note_date: continue
                    note_date = reformat_dates(note_date.split(' ')[0])  # after space is the time
                    if not note_date: continue
                    note_date_seconds = convert_timestamp_to_seconds(note_date)
                    for criteria in empi_to_date_range[empi]:
                        # save the patient data within the desired range
                        if (note_date_seconds >= criteria['start'] and
                                note_date_seconds <= criteria['end']) and criteria['include']==1:
                            data.append(fields)
                fields = []
            else:
                report.append(line)
    data = pd.DataFrame(data, columns=header)
    output_fname =  os.path.join(
        os.path.dirname(sys.argv[0]),
        '%s_filter_%s-%s.csv'%(input_fname.split('.')[0], str(days_before), str(days_after)))
    data.to_csv(output_fname, index=False)

    return "done"

def rpdr_to_csv(input_fname):
    with open(input_fname, 'r') as file:
        data, header, fields = [], [], []
        for line in file:
            line = line.rstrip()
            if line.strip() == '':
                continue
            if not header:
                if line.count('|') < 8:
                    return "error"
                header = [field.lower().strip()
                        for field in line.split('|')]
                continue
            if not fields and '|' in line:
                fields = [field.lower().strip()
                        for field in line.split('|')]
                fields[-1] = line
                report = []
            elif 'report_end' in line:
                report.append(line)
                fields[-1] += '\n'.join(report)
                data.append(fields)
                fields = []
            else:
                report.append(line)
    data = pd.DataFrame(data, columns=header)
    output_fname =  os.path.join(
        os.path.dirname(sys.argv[0]),
        input_fname.split('.')[0] + '.csv')
    data.to_csv(output_fname, index=False)

    return "done"