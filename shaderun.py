from shade import *

simple_logging(debug=True)
conn = openstack_cloud(cloud='myfavoriteopenstack')

image_id = '7ad5923c-7b52-4749-49c1-bc1632b2892a'
image = conn.get_image(image_id)

flavor_id = '921e54d6a-9ead-3415-b8d5-81593d3aea5c'
flavor = conn.get_flavor(flavor_id)

instances = conn.list_servers()
for inst in instances:
    print(inst)

instance_name = 'test'
testing_instance = conn.create_server(wait=True, auto_ip=True,
    name=instance_name,
    image=image_id,
    flavor=flavor_id)
print(testing_instance)

print('Checking for existing SSH keypair...')
keypair_name = 'demokey'
pub_key_file = '/home/cloud/.ssh/id_rsa.pub'

if conn.search_keypairs(keypair_name):
    print('Keypair already exists. Skipping import.')
else:
    print('Adding keypair...')
    conn.create_keypair(keypair_name, open(pub_key_file, 'r').read().strip())

for keypair in conn.list_keypairs():
    print(keypair)

print('Checking for existing security groups...')
sec_group_name = 'all-in-one'
if conn.search_security_groups(sec_group_name):
    print('Security group already exists. Skipping creation.')
else:
    print('Creating security group.')
    conn.create_security_group(sec_group_name, 'network access for all-in-one application.')
    conn.create_security_group_rule(sec_group_name, 80, 80, 'TCP')
    conn.create_security_group_rule(sec_group_name, 22, 22, 'TCP')

conn.search_security_groups(sec_group_name)

ex_userdata = '''#!/usr/bin/env bash

curl -L -s https://git.openstack.org/cgit/openstack/faafo/plain/contrib/install.sh | bash -s -- \
-i faafo -i messaging -r api -r worker -r demo
'''

instance_name = 'one-in-all'
testing_instance = conn.create_server(wait=True, auto_ip=False,
    name=instance_name,
    image=image_id,
    flavor=flavor_id,
    key_name=keypair_name,
    security_groups=[sec_group_name],
    userdata=ex_userdata)

f_ip = conn.available_floating_ip()

conn.add_ip_list(testing_instance, [f_ip['floating_ip_address']])

print('The Fractals app will be deployed to http://%s' % f_ip['floating_ip_address'] )