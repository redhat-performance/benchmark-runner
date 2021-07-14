
import os

# when adding new environment variables update environment_variables_dict
environment_variables_dict = {}

workloads_list = ['hammerdb_pod_mariadb', 'hammerdb_pod_mssql', 'hammerdb_pod_postgres',
                  'hammerdb_vm_mariadb', 'hammerdb_vm_mssql', 'hammerdb_vm_postgres',
                  'stressng_pod', 'stressng_vm',
                  'uperf_pod', 'uperf_vm']

# os.environ['KUBECONFIG'] = ''
environment_variables_dict['kubeconfig'] = os.environ.get('KUBECONFIG', '')

# os.environ['KUBEADMIN_PASSWORD'] = ''
environment_variables_dict['kubeadmin_password'] = os.environ.get('KUBEADMIN_PASSWORD', '')

#os.environ['WORKLOAD'] = 'stressng_pod'
environment_variables_dict['workload'] = os.environ.get('WORKLOAD', '')

#os.environ['ELASTICSEARCH'] = ''
environment_variables_dict['elasticsearch'] = os.environ.get('ELASTICSEARCH', '')

#os.environ['ELASTICSEARCH_PORT'] = ''
environment_variables_dict['elasticsearch_port'] = os.environ.get('ELASTICSEARCH_PORT', '')

# node selectors
#os.environ['PIN_NODE1'] = ''
environment_variables_dict['pin_node1'] = os.environ.get('PIN_NODE1', '')

# i.e. uperf server node
#os.environ['PIN_NODE2'] = ''
environment_variables_dict['pin_node2'] = os.environ.get('PIN_NODE2', '')
