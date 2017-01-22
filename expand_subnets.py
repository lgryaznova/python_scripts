#!/usr/bin/env python3

"""
This module takes a list of IPv4 subnets from a file
specified by the user (with each subnet on a new line),
gets a list of usable host addresses of each subnet and
writes all these hosts to an output file specified
by the user (each host on a new line).

If a host address is given instead of the subnet address,
the corresponding subnet address is used instead with no
exception thrown. However, the error message will be displayed.
If the input file contains info other than IPv4 addresses,
only IPv4 addresses will be processed and other lines will
be omitted with the error message displayed as well.

The script must be in the same folder as the input file,
the output file will be located in it with extention ".out"
unless other name is specified by user.

Usage: ./expand_subnets.py <file_with_subnets>
file_with_subnets - name of the file with a list of IPv4 subnets
"""
import ipaddress
import os
import sys


# user interface
def usage():
    """
    Displays how to use the script
    """
    print('\n\
*****************************************************************\n\
This module takes a list of IPv4 subnets from a file\n\
specified by the user (with each subnet on a new line),\n\
gets a list of usable host addresses of each subnet and\n\
writes all these hosts to an output file specified\n\
by the user (each host on a new line).\n\n\
If a host address is given instead of the subnet address,\n\
the corresponding subnet address is used instead with no\n\
exception thrown. However, the error message will be displayed.\n\
If the input file contains info other than IPv4 addresses,\n\
only IPv4 addresses will be processed and other lines will\n\
be omitted with the error message displayed as well.\n\n\
The script must be in the same folder as the input file,\n\
the output file will be located in it with extention ".out"\n\
unless other name is specified by user.\n\n\
Usage: ./expand_subnets.py <file_with_subnets>\n\
file_with_subnets - name of the file with a list of IPv4 subnets\n\
*****************************************************************\n')


# generator to be used to write directly to the output file to save memory
def hosts_generator(input_list):
    """
    net_list - list of subnets (IPv4Network class instances)

    Returns a generator of hosts in string representation ending with
    a newline symbol.
    """
    for subnet in input_list:
        for i in subnet.hosts():
            yield str(i) + '\n'


def body(f_input):
    """
    Main function, processes the input textfile with IPv4 subnets
    and writes the result into the output file.

    f_input - textfile to process

    The output file is named f_input + '.out'
    """
    f_output = f_input + ".out"
    choice = ''
    while choice != 'y':
        if os.path.exists(f_output):
            choice = input('File already exists. Do you want to overwrite it? y/n ')
            if choice == 'n':
                f_output = input('Enter the name for the output file: ')
            elif choice != 'y':
                print('Cannot recognize your answer. To exit script press Ctrl-C.')
        else:
            break
    print('\nProcessing...\n')

    # read in the list of subnets
    netlist = []
    with open(f_input, 'r') as tempfile:
        for line in tempfile:
            netlist.append(line.strip(' \n\t'))

    # convert all items in the list into valid subnet addresses, mark errors
    invalid_lines = []
    for i, elem in enumerate(netlist):
        try:
            netlist[i] = ipaddress.ip_network(elem, strict=True)
        except ValueError as ex1:
            # if it's a host address, get the network address and log warning
            try:
                netlist[i] = ipaddress.ip_network(elem, strict=False)
                print('Warning: {0}. {1} is used instead.'.format(
                    str(ex1), str(netlist[i].network_address)))
            # if not an IPv4 address, mark as error and log the error
            except ValueError as ex2:
                invalid_lines.append(i)
                # empty strings are omitted without logging
                if netlist[i] != '':
                    print('Invalid subnet address: {0}.'.format(str(ex2)))

    # delete invalid elements of the list of subnets
    if invalid_lines:
        for i in invalid_lines[::-1]:
            del netlist[i]

    # write output file
    with open(f_output, 'w') as outfile:
        outfile.writelines(hosts_generator(netlist))

    print('\nDone!\n')


if __name__ == '__main__':
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        body(sys.argv[1])
    else:
        usage()
