wget https://cloud.centos.org/centos/9-stream/x86_64/images/CentOS-Stream-GenericCloud-x86_64-9-20240527.0.x86_64.qcow2
https://linuxize.com/post/how-to-install-postgresql-on-centos-8/
# run inside the container disk
$ dnf -y update
$ dnf -y install postgresql.x86_64 postgresql-contrib.x86_64 postgresql-server.x86_64
$ sudo postgresql-setup initdb

$ sudo systemctl start postgresql
$ sudo systemctl status postgresql
$ sudo systemctl stop postgresql
$ sudo systemctl enable postgresql

rm /var/lib/pgsql/data/pg_hba.conf
vi /var/lib/pgsql/data/pg_hba.conf

# TYPE  DATABASE        USER            ADDRESS                 METHOD
# "local" is for Unix domain socket connections only
local   all             all                                     trust
# IPv4 local connections:
host    all             all             all            trust
Or
echo local   all             all                                     trust > /var/lib/pgsql/data/pg_hba.conf
echo host    all             all             all            trust >> /var/lib/pgsql/data/pg_hba.conf

$ vi /var/lib/pgsql/data/postgresql.conf (according to pod)
Or
echo max_connections = 100 > /var/lib/pgsql/data/postgresql.conf
echo max_prepared_transactions = 0 >> /var/lib/pgsql/data/postgresql.conf
echo shared_buffers = 4096MB >> /var/lib/pgsql/data/postgresql.conf
echo effective_cache_size = 8192MB >> /var/lib/pgsql/data/postgresql.conf

$ sudo systemctl start postgresql
$ sudo systemctl status postgresql
$ echo "alter role postgres password 'postgres'" > input
$ psql -U postgres -d postgres < input
