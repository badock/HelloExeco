from execo import *
from execo_g5k import *
import os
import sys
import jinja2

# job_id = 106335
job_id = 106368
site = "nantes"
env_name = "debian9-x64-nfs"
do_deployement = True


def render_template(template_path, variables):
    path, filename = os.path.split(template_path)
    result = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(variables)
    return result


def generate_file_from_template(template_path, variables, output_path):
    output_str = render_template(template_path, variables)
    with open(output_path, mode="w") as f:
        f.write(output_str)
        return output_path
    return None


if __name__ == "__main__":

    print("======= Create a tmp folder =======")
    result_directory = "tmp"
    if not os.path.exists(result_directory):
        os.makedirs(result_directory)
    print("OK")

    print("======= View reservations information =======")
    infos = get_oar_job_info(job_id, site)
    for info in infos:
        print(" * %s --> %s" % (info, infos[info]))
    print("OK")

    print("======= List nodes =======")
    nodes = get_oar_job_nodes(job_id, site)
    for node in nodes:
        print(" * "+node.address)
    print("OK")

    if do_deployement:
        print("======= Deploy an environment on nodes =======")
        deployment = Deployment(hosts=nodes, env_name=env_name)
        deployed_hosts = deploy(deployment, num_tries=3)
        print(deployed_hosts)
        print("OK")

    print("======= Upload a script to contextualize nodes =======")
    conn_params = {'user': 'root'}
    cmd_runnable = Put(nodes,
                       ["script/prepare_experiment.sh"],
                       remote_location=".",
                       connection_params=conn_params)
    cmd_runnable.run()
    print("OK")

    print("======= Upload a script to contextualize nodes =======")
    is_master = True
    master_node = None
    for node in nodes:
        if is_master:
            master_node = node
        generate_file_from_template("templates/launch_experiment.sh.jinja2",
                                    {
                                        "is_master": is_master,
                                        "master_node": master_node,
                                        "nodes": nodes,
                                        "node": node
                                    },
                                    "tmp/launch_experiment.sh")
        cmd_runnable = Put(node,
                           ["tmp/launch_experiment.sh"],
                           remote_location="launch_experiment.sh",
                           connection_params=conn_params)
        cmd_runnable.run()
        is_master = False
    print("OK")

    print("======= Preparing nodes for an experiment =======")
    cmd = "bash prepare_experiment.sh"
    cmd_runnable = Remote(cmd, nodes, conn_params)
    cmd_runnable.run()
    print("OK")

    print("======= Running a script on nodes =======")
    cmd = "bash launch_experiment.sh"
    cmd_runnable = Remote(cmd, nodes, conn_params)
    cmd_runnable.run()
    print("OK")

    print("======= Download the result of the script from nodes =======")
    result_directory = "results"
    if not os.path.exists(result_directory):
        os.makedirs(result_directory)
    conn_params = {'user': 'root'}

    for node in nodes:
        local_location = result_directory+"/"+node.address.replace(".", "_").replace("-", "_")
        cmd_runnable = Get(node,
                           ["output.log"],
                           local_location=local_location,
                           connection_params=conn_params)
        cmd_runnable.run()
    print("OK")

    sys.exit(0)
