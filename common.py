import datetime

def reformat_timestamp(timestamp):
    in_format = '%Y-%m-%d %H:%M:%S'
    out_format = '%d %B, %Y'
    time = datetime.datetime.strptime(timestamp, in_format)
    return time.strftime(out_format)
