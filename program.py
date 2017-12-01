import execo
import execo_g5k
from execo import *
from execo_g5k import *
from execo_engine import *
import time
import os

job_id = 67856
site = "nantes"
env_name = "jessie-x64-min"

do_deployement = True

print("======= View reservations information =======")
infos = get_oar_job_info(job_id, site)
for info in infos:
    print(" * %s --> %s" % (info, infos[info]))

print("======= List nodes =======")
nodes = get_oar_job_nodes(job_id, site)
for node in nodes:
    print(" * "+node.address)

if do_deployement:
    print("======= Deploy an environment on nodes =======")
    deployment = Deployment(hosts=nodes, env_name=env_name)
    deployed_hosts = deploy(deployment, num_tries=3)
    print(deployed_hosts)

print("======= Upload a local script on nodes =======")
conn_params = {'user': 'root'}
cmd_runnable = Put(nodes,
                   ["script/launch_experiment.sh"],
                   remote_location="launch_experiment.sh",
                   connection_params=conn_params)
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
                       ["output.txt"],
                       local_location=local_location,
                       connection_params=conn_params)
    cmd_runnable.run()
print("OK")