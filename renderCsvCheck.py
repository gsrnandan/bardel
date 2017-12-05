import argparse
import os
import sys
import warnings
import csv
import errno


# Flags
enum_flags = {
"app" : 1,
"renderer" : 2,
"failed" : 4
}

filter_flags = ["app","renderer","failed"]

def calculate_avgtime(file_path):
    render_times = []
    try:
        with open(file_path) as f:
            csv_data = csv.reader(f, delimiter=',')
            for row in csv_data:
                render_times.append(int(row[5])) 
    except IOError:
        raise 'File path for csv is invalid'

    return sum(render_times) / len(render_times)


def get_arguments():
    parser = argparse.ArgumentParser('Csv File Parser')
    parser.add_argument('filepath',nargs='?',action='store',type=str)
    parser.add_argument('-app', action='store', type=str)
    parser.add_argument('-renderer', action='store', type=str)
    parser.add_argument('-failed', action='store', type=bool,default = False)
    parser.add_argument('-avgtime', action='store', type=str)
    parser.add_argument('-avgcpu', action='store', type=str)
    parser.add_argument('-avgram', action='store', type=str)
    parser.add_argument('-maxram', action='store', type=str)
    parser.add_argument('-maxcpu', action='store', type=str)
    parser.add_argument('-summary', action='store', type=str)
    return vars(parser.parse_args())


def check_flags(args):
    flags = 0;
    for arg in args:
        print arg
        if args[arg] and arg != "filepath":
            flags = flags | enum_flags[arg]
    print flags
    return flags


def parse_csv_files(file_paths, flags_in_args):
        for file_path in file_paths:
            print 'Parsing {}'.format(file_path)
            try:
                with open(file_path) as f:
                    csv_data = csv.reader(f, delimiter=',')
                    for row in csv_data:
                        if flags_in_args:
                            if any(flag in flags_in_args for flag in filter_flags):
                                if all(data in row for data in flags_in_args.values()):
                                    print row
                        else:
                            print row
            except IOError:
                warnings.warn('File path for csv is invalid')


def parse_flags(flags):
    flags_in_args = {}
    args = get_arguments()
    for flag in enum_flags:
        if (flags & enum_flags[flag]):
            flags_in_args[flag] = args[flag]
    print flags_in_args
    return flags_in_args 

def scan_for_csv():

    print "No file Path argument found, Parsing through the current directory"
    current_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.dirname(current_dir)
    print 'Scanning for csv files in folder {}'.format(parent_dir)
    return [os.path.join(parent_dir,file) for file in os.listdir(parent_dir) if file.endswith('.csv')]

if __name__ == '__main__':
    args = get_arguments()
    print args
    flags = check_flags(args)
    csv_file_paths = [args['filepath']] if args['filepath'] else scan_for_csv()
    if not csv_file_paths:
         warnings.warn('Csv Files not found')
         sys.exit(errno.EINVAL)
    parse_csv_files(csv_file_paths, parse_flags(flags))

