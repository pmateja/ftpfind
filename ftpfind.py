#!/usr/bin/env python3

import os
import sys
import ftplib
import netrc
import argparse
import datetime
import signal
from dateutil.relativedelta import relativedelta
import re


def get_auth_from_netrc(host):
    n = netrc.netrc()
    user, account, password = n.authenticators(host)
    return user, password


def get_current_date():
    return datetime.datetime.now()


def val_to_int(s):
    try:
        return int(s)
    except:
        return 0


def parse_date(s):
    re_delta = re.compile("^(\d+)y|(\d+)m|(\d+)d$")
    re_one_day = re.compile("^\d{4}-\d{2}-\d{2}$")
    if re.match(re_one_day, s):
        start, stop = get_start_stop_day_dates(s)
    elif re.match(re_delta, s):
        stop = datetime.datetime.now()
        start = substr_date(stop, **parse_date_delta(s))
    else:
        raise ValueError()
    return start, stop


def parse_date_delta(s):
    re_delta = re.compile("^(\d+)y|(\d+)m|(\d+)d$")
    schema = ("years", "months", "days")
    try:
        val = [val_to_int(i) for i in re.match(re_delta, s).groups()]
    except:
        val = (0, 0, 0)
    return dict(zip(schema, val))


def substr_date(date, days=0, months=0, years=0):
    return date - relativedelta(days=days, months=months, years=years)


def get_start_stop_day_dates(s):
    d = datetime.datetime.strptime(s, "%Y-%m-%d")
    return d.replace(hour=0, minute=0, second=0), d.replace(hour=23, minute=59, second=59)


def connect(host, user, password, port):
    ftp = ftplib.FTP()
    ftp.connect(host=host, port=port)
    ftp.login(user=user, passwd=password)
    return ftp


def walk(ftp, root):
    for i in ftp.mlsd(root):
        if i[1]['type'] == "file":
            item = [os.path.join(root, i[0]), i[1]]
            yield item
        elif i[1]['type'] == "dir":
            yield from walk(ftp, os.path.join(root, i[0]))


def date_filter(start, stop):
    date_format = "%Y%m%d%H%M%S"
    def filter(item):
        s = item[1]["modify"]
        d = datetime.datetime.strptime(s, date_format)
        return start <= d <= stop
    return filter


def regexp_filter(regexp):
    r = re.compile(regexp)
    def filter(item):
        s = item[0]
        result = re.findall(r, s)
        return bool(result)
    return filter


def item_printer(method="simple"):
    def simple_print(item):
        print(item[0])
    def full_print(item):
        print(item[0], item[1])
    if method == "simple":
        return simple_print
    else:
        return full_print


def handler(signum, frame):
    sys.exit()


def init_parser():
    parser = argparse.ArgumentParser(prog="ftpfind")
    parser.add_argument("--user", "-u", help="FTP user name")
    parser.add_argument("--password", "-p", help="FTP password")
    parser.add_argument("--port", "-P", type=int, metavar="1-65535", choices=range(1, 65535), help="FTP port", default=21)
    parser.add_argument("--path", "-d", help="Searching root path", default="/")
    parser.add_argument("--regexp", "-s", help="Pattern for regular expression")
    parser.add_argument("--time", "-t", help="Creation time")
    parser.add_argument("--type", choices=("file", "directory", "all"), default="all", help="File or directory")
    parser.add_argument("--limit", type=int, help="Stop searching after limit reached")
    parser.add_argument("--format", choices=("simple", "full"), default="simple", help="File list format")
    parser.add_argument("host", help="Remote ftp server name")
    return parser.parse_args()


def main(args):
    signal.signal(signal.SIGINT, handler)
    args = init_parser()
    host = args.host
    port = args.port
    user, password = get_auth_from_netrc(host)
    if args.user is not None:
        user = args.user
    if args.password is not None:
        password = args.password
    filters = []
    if args.time:
        t1, t2 = parse_date(args.time)
        filters.append(date_filter(t1, t2))
    if args.regexp:
        filters.append(regexp_filter(args.regexp))
    limit = args.limit
    printer = item_printer(args.format)
    ftp = connect(host, user, password, port)
    for i, item in enumerate(walk(ftp, args.path)):
        if all([f(item) for f in filters]):
            if limit is not None and i  == limit:
                break
            printer(item)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[:]))
