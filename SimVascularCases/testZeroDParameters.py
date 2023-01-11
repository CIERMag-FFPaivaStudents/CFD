#Author: Gustavo Solcia
#E-mail: gustavo.solcia@usp.br

"""Test code for parameter change in SimVascular ZeroDSolver.
"""

import os
import sys
import json
import copy
import numpy as np
import svzerodsolver
from tqdm import tqdm
import matplotlib.pyplot as plt

def run_custom_0d_simulation(file_path,save_results_all, randomize_RCR):
    """ Custom function to run and change simulation parameters. 
    """
    custom_0d_elements = None

    with open(file_path, 'r') as infile:
        parameters = json.load(infile)

    svzerodsolver.solver.create_LPN_blocks(parameters, custom_0d_elements)
    svzerodsolver.solver.set_solver_parameters(parameters)

    simulation_start_time = 0.0

    block_list = list(parameters["blocks"].values())
    connect_list, wire_dict = svzerodsolver.connections.connect_blocks_by_inblock_list(block_list)
    neq = svzerodsolver.connections.compute_neq(block_list, wire_dict) # number of equations governing the 0d model
    for block in block_list: # run a consistency check
        svzerodsolver.connections.check_block_connection(block)
    var_name_list = svzerodsolver.connections.assign_global_ids(block_list, wire_dict) # assign solution variables with global ID
    y_initial, ydot_initial = svzerodsolver.connections.initialize_solution_structures(neq)

    y_next = y_initial.copy()
    ydot_next = ydot_initial.copy()

    rho = 0.1
    args = {}
    args['Time step'] = parameters["simulation_parameters"]["delta_t"]
    args['rho'] = rho
    args['Wire dictionary'] = wire_dict
    args["check_jacobian"] = False #using the default config from setup_and_run_0d_simulation

    print('Starting simulation')

    ylist = [y_next.copy()]
    parameters["initial_time"] = simulation_start_time
    tlist = np.array([ parameters["initial_time"] + _*parameters["simulation_parameters"]["delta_t"] for _ in range(0, parameters["simulation_parameters"]["total_number_of_simulated_time_steps"])])

    # create time integration
    t_int = svzerodsolver.solver.time_int.GenAlpha(rho, y_next)

    if 'tqdm' in sys.modules:
        loop_list = tqdm(tlist[:-1])
    else:
        loop_list = tlist[:-1]

    outlet_vessels_of_model = svzerodsolver.solver.use_steady_bcs.get_ids_of_cap_vessels(parameters, "outlet")
    vessel_id_to_boundary_condition_map = parameters["vessel_id_to_boundary_condition_map"] 

    name_list = ['BC'+str(vessel_id)+'_outlet' for vessel_id in outlet_vessels_of_model]
    
    for t_current in loop_list:
        if randomize_RCR:
            for i,block in enumerate(block_list):
                if block.name in name_list:
                    Rp_rnd = block_list[i].Rp_func(t_current) + 1e1*np.random.normal()
                    C_rnd = block_list[i].C_func(t_current) + 1e-6*np.random.normal() #smaller changes in compliance
                    Rd_rnd = block_list[i].Rd_func(t_current) + 1e0*np.random.normal()
                    block_list[i].Rp_func = svzerodsolver.solver.create_unsteady_bc_value_function([0.0, 1.0], [Rp_rnd, Rp_rnd])
                    block_list[i].C_func = svzerodsolver.solver.create_unsteady_bc_value_function([0.0, 1.0], [C_rnd, C_rnd])
                    block_list[i].Rd_func = svzerodsolver.solver.create_unsteady_bc_value_function([0.0, 1.0], [Rd_rnd, Rd_rnd])
        args['Solution'] = y_next
        y_next, ydot_next = t_int.step(y_next, ydot_next, t_current, block_list, args, parameters["simulation_parameters"]["delta_t"])
        ylist.append(y_next)

        var_name_list_original = copy.deepcopy(var_name_list)
        results_0d = np.array(ylist)
        zero_d_time = tlist
        zero_d_input_file_name = os.path.splitext(file)[0]
        if randomize_RCR:
            zero_d_input_file_name += '_randomRCR'

    if save_results_all:
        zero_d_simulation_results_file_path = zero_d_input_file_name + "_all_results"
        zero_d_results = svzerodsolver.solver.reformat_network_util_results_all(zero_d_time, results_0d, var_name_list)
        np.save(zero_d_simulation_results_file_path, zero_d_results)
    print("0D simulation completed!\n")


if __name__=='__main__':
    path = 'CarotidArtery_0D'
    input = 'solver_0d.in'

    save_results_all = True

    file = os.path.join(path, input)

    run_custom_0d_simulation(file, save_results_all, randomize_RCR=False)
    run_custom_0d_simulation(file, save_results_all, randomize_RCR=True) #Using random parameters

    data = np.load(os.path.join(path, 'solver_0d_all_results.npy'), allow_pickle=True)
    
    flow_data = data.item().get('flow')
    time = data.item().get('time')

    data_random = np.load(os.path.join(path, 'solver_0d_randomRCR_all_results.npy'), allow_pickle=True)
    flow_data_random = data_random.item().get('flow')

    plt.figure()
    plt.plot(time,flow_data_random['Q_V3_BC3_outlet'], color='gray', label='Q_V3_BC3_outlet_random')
    plt.plot(time, flow_data['Q_V3_BC3_outlet'], color='k', label='Q_V3_BC3_outlet')
    plt.plot(time, flow_data_random['Q_V6_BC6_outlet'], linestyle ='dashed', color='gray', label='Q_V6_BC6_outlet_random')
    plt.plot(time, flow_data['Q_V6_BC6_outlet'], linestyle = 'dashed' , color='k', label='Q_V6_BC6_outlet')
    plt.legend()
    plt.show()
