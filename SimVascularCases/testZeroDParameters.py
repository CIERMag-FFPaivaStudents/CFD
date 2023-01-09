#Author: Gustavo Solcia
#E-mail: gustavo.solcia@usp.br

"""Test code for parameter change in SimVascular ZeroDSolver.
"""

import os
import svzerodsolver
import json

def run_custom_0d_simulation(file_path):
    """ Custom function to run and change simulation parameters. 
    """
    custom_0d_elements = None

    with open(file_path, 'r') as infile:
        parameters = json.load(infile)


    svzerodsolver.solver.create_LPN_blocks(parameters, custom_0d_elements)

    print(parameters.keys())
    print(len(parameters['boundary_conditions']))
    print(parameters['boundary_conditions'][1]['bc_values'])
    print(parameters['boundary_conditions'][2]['bc_values'])
    #run_network_util

    return


if __name__=='__main__':
    path = 'CarotidArtery_0D'
    input = 'solver_0d.in'

    file = os.path.join(path, input)

    #svzerodsolver.solver.set_up_and_run_0d_simulation(file)
    run_custom_0d_simulation(file)

