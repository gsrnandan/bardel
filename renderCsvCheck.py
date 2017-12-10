import argparse
import os
import sys
import warnings
import csv
import errno

from renderStatistics import RENDER_STATISTICS

class RENDER_CSV_CHECK:
    
    def __init__(self):
    
        
        # The set of flags that filter the rows of input
        self.filter_flags = ["app",
                        "renderer",
                        "failed",
                    ]

        # The set of flags that need calculation of value before display
        self.display_flags =  {"avgtime":"calculate_avg",
                                "avgcpu":"calculate_avg",
                                "avgram":"calculate_avg",
                                "maxram":"get_max",
                                "maxcpu":"get_max",
                            }

        self.render_stats = []
        self.init_render_statistics()

    def init_render_statistics(self):

        # Create a render statistic object for all the required stats
        self.render_times = RENDER_STATISTICS("time",5,"avgtime")
        self.render_stats.append(self.render_times)
        self.cpu_percentage = RENDER_STATISTICS("cpu",7,"avgcpu","maxcpu")
        self.render_stats.append(self.cpu_percentage)
        self.ram_used = RENDER_STATISTICS("ram",6,"avgram","maxram")
        self.render_stats.append(self.ram_used)

    def reset_render_stats(self):
        for stats in self.render_stats:
            stats.reset_data()



    def get_arguments(self):
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


    def parse_csv_files(self,file_paths, flags_in_args):
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

            
            print 'Parsing {}'.format(file_path)
            
            try:
                with open(file_path) as f:
                    csv_data = csv.reader(f, delimiter=',')
                    for row in csv_data:
                        # Check if any filter flags are set and then read the lines correspondingly 
                        if any(flag in flags_in_args for flag in self.filter_flags):
                            # Store the value passed from the filter flags and check them in the row
                            filter_flag_values = [flags_in_args[flag] for flag in self.filter_flags if flag in flags_in_args]
                            if all(data in row for data in filter_flag_values):
                                print row

                        # Append the render time, ram and cpu data
                        self.render_times.data.append(float(row[self.render_times.row]))
                        self.ram_used.data.append(float(row[self.ram_used.row]))
                        self.cpu_percentage.data.append(float(row[self.cpu_percentage.row]))

                    # Check if display flags are set and call the corresponding function
                    if any(flag in flags_in_args for flag in self.display_flags):
                        # Call the display functions
                        self.display_values(flags_in_args,self.display_flags)
                    
                    # Reset the render stats for each file
                    self.reset_render_stats()



            except IOError:
                warnings.warn('File path for csv is invalid')


    def display_values(self,flags_in_args,value_flags):
        """ Method to display the average and max values of the render statistics

            This method checks the value flags that are set and then calculates 
            the corresponding render statistics

            Args:
                flags(dict): dictionary of the command line arguments passed
                             and their values
                args(list): lists of the render statistics

        """
        for stats in self.render_stats:
            for flag in stats.associated_flags:
                if flag in flags_in_args:
                    func = value_flags[flag]
                    print getattr(stats, func)()
                

    def parse_flags(self,args):
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

    def scan_for_csv(self):
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
    render_check = RENDER_CSV_CHECK()
    args = render_check.get_arguments()
    print args
    csv_file_paths = [args['filepath']] if args['filepath'] else render_check.scan_for_csv()
    if not csv_file_paths:
         warnings.warn('Csv Files not found')
         sys.exit(errno.EINVAL)
    render_check.parse_csv_files(csv_file_paths, render_check.parse_flags(args))

