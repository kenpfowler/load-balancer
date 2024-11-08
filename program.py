import getopt, sys
from Server import Server

# Remove 1st argument from the
# list of command line arguments
argument_list = sys.argv[1:]

# Options
options = "hmo:"

# Long options
long_options = ["Help", "My_file", "Output="]

try:
    # Parsing argument
    arguments, values = getopt.getopt(argument_list, options, long_options)
    
    # checking each argument
    for currentArgument, currentValue in arguments:

        if currentArgument in ("-h", "--Help"):
            print ("Displaying Help")
            
        elif currentArgument in ("-m", "--My_file"):
            print ("Displaying file_name:", sys.argv[0])
            
        elif currentArgument in ("-o", "--Output"):
            print (("Enabling special output mode (% s)") % (currentValue))
            
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))


server = Server()

server.start()