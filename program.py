import getopt, sys
from LoadBalancer import LoadBalancer

# Remove 1st argument from the
# list of command line arguments
argument_list = sys.argv[1:]

# Options
options = "hps:"

# Long options
long_options = ["host=", "port=", "servers="]

host = "localhost"
port = 8080

def split_address(address):
    host, port = address.split(":")
    return [host, int(port), True]


try:
    # Parsing argument
    arguments, values = getopt.getopt(argument_list, options, long_options)
    
    # checking each argument
    for current_argument, current_value in arguments:

        if current_argument in ("-h", "--host"):
            host = current_value
            print (("specified host (% s)") % (current_value))
            
        elif current_argument in ("-p", "--port"):
            port = int(current_value)
            print (("specified port (% s)") % (current_value))

        elif current_argument in ("-s", "--servers"):
            raw_address = current_value.split(",")
            servers = list(map(split_address, raw_address))
            
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))


load_balancer = LoadBalancer(host, port, servers)

load_balancer.start()