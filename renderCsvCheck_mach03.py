import argparse
import os
import sys
import warnings
import csv
import errno

class RENDER_STATISTICS:
    def __init__(self,name,row):
    self.flagName = name
    self.data = []
    self.displayFlag = False
    self.row = row

    def calculate_avg(self):
        if self.data:
            total_sum = 0
            for val in self.data:
                total_sum += val
            return total_sum / len(self.data)

    def get_max(self):
        return max(self.data)

def calculate_avg(values):
    print "Inside Calculate"
    if values:
        total_sum = 0
        for value in values:
            total_sum += value

        return total_sum / len(values)

def get_max(values):
    return max(values)


render_times = []
ram_used = []
cpu_percentage = []

# The set of flags that filter the rows of input
filter_flags = ["app",
                "renderer",
                "failed",
            ]


# The set of flags that need calculation of value before display
value_flags = {"avgtime":{"row":5,"flagFunc":calculate_avg,"flagList":render_times},
                "avgcpu":{"row":7,"flagFunc":calculate_avg,"flagList":cpu_percentage},
                "avgram":{"row":6,"flagFunc":calculate_avg,"flagList":ram_used},
                "maxram":{"row":6,"flagFunc":get_max,"flagList":None},
                "maxcpu":{"row":7,"flagFunc":get_max,"flagList":None},
            }


def get_arguments():
    """ Method to parse all the command line arguments

        This function reads the command line arguments passed and 
        creates a dictionary from it

        Returns:
            args(dict): The dictionary with the arguments and their
                        values

    """
    parser = argparse.ArgumentParser('Csv File Parser')
    parser.add_argument('filepath',nargs='?',action='store',type=str)
    parser.add_argument('-app', action='store', type=str)
    parser.add_argument('-renderer', action='store', type=str)
    parser.add_argument('-failed', action='store_true')
    parser.add_argument('-avgtime', action='store_true')
    parser.add_argument('-avgcpu', action='store_true')
    parser.add_argument('-avgram', action='store_true')
    parser.add_argument('-maxram', action='store_true')
    parser.add_argument('-maxcpu', action='store_true')
    parser.add_argument('-summary', action='store_true')
    return vars(parser.parse_args())


def parse_csv_files(file_paths, flags_in_args):
    """ Method to parse the csv files

        This function parses the csv files that are either passed 
        in the arguments, or either in the current directory. It uses
        the flags to filter the data to display.

        Args:
            file_paths(list): list of the file paths for the csv files
                                that are to be parsed
            flags_in_args(dict): a dictionary of the flags that are
                                 passed in the command line and their
                                 values

    """

    
    # Open the files
    for file_path in file_paths:

        # Create list for the time, ram and cpu usage
        stats = []
        render_times = RENDER_STATISTICS("time")
        cpu_percentage = RENDER_STATISTICS("cpu")
        ram_used = RENDER_STATISTICS("ram")

        print 'Parsing {}'.format(file_path)
        
        try:
            with open(file_path) as f:
                csv_data = csv.reader(f, delimiter=',')
                for row in csv_data:
                    # If none of the flags are set, just print the row with a successful render
                    # if not flags_in_args and "True" in row:
                    #     print row
                    #     continue

                    # else:
                    # Check if any filter flags are set and then read the lines correspondingly 
                    if any(flag in flags_in_args for flag in filter_flags):
                        if all(data in row for data in flags_in_args.values()):
                            print row

                    # Append the render time, ram and cpu data
                    render_times.data.append()
                    # value_flags["avgtime"]["flagList"].append(row[[value_flags]["avgtime"]["row"]])
                    # render_times.append(row[value_flags["avgtime"][0]])
                    # print "render_times", render_times
                    # ram_used.append(row[value_flags["avgram"][0]])
                    # cpu_percentage.append(row[value_flags["avgcpu"][0]])

                display_values(flags_in_args,value_flags)


        except IOError:
            warnings.warn('File path for csv is invalid')


def display_values(flags_in_args,render_times,ram_used,cpu_percentage):
    """ Method to display the average and max values of the render statistics

        This method checks the value flags that are set and then calculates 
        the corresponding render statistics

        Args:
            flags(dict): dictionary of the command line arguments passed
                         and their values
            args(list): lists of the render statistics

    """
    for flag in flags_in_args: 
        if flag in value_flags:
            statisticsList = value_flags[flag][2]
            print value_flags[flag][1](statisticsList) 




def parse_flags(args):
    """ Method to parse through all the command line arguments.

        This functions iterates through all the arguments in the args list 
        and creates a dictionay with the flags that have some value set

        Args:
            args(dict): a dictionary with all the command line arguments
                        this function can take

    """
    # Iterating through all the values of the args excpet for the filepath
    flags_in_args = {flag: val for flag,val in args.iteritems() if val and flag != "filepath"}
    
    # Check for the Success flag if the failed flag is set, 
    # set the value for its corresponding render Success column to false
    if "failed" in flags_in_args.keys():
        flags_in_args["failed"] = "False"
    else:
        flags_in_args["failed"] = "True"
    print flags_in_args
    return flags_in_args 

def scan_for_csv():
    """ Method to scan the curent directory for csv file.

        This function parses through the current directory from where the 
        script is run to check for valid csv files, when no file argument
        is passed explicitly

    """

    print "No file Path argument found, Parsing through the current directory"
    current_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.dirname(current_dir)
    print 'Scanning for csv files in folder {}'.format(parent_dir)
    return [os.path.join(parent_dir,file) for file in os.listdir(parent_dir) if file.endswith('.csv')]

if __name__ == '__main__':
    args = get_arguments()
    print args
    csv_file_paths = [args['filepath']] if args['filepath'] else scan_for_csv()
    if not csv_file_paths:
         warnings.warn('Csv Files not found')
         sys.exit(errno.EINVAL)
    parse_csv_files(csv_file_paths, parse_flags(args))

