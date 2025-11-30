wget https://cloud.centos.org/centos/9-stream/x86_64/images/CentOS-Stream-GenericCloud-x86_64-9-20240527.0.x86_64.qcow2
https://mariadb.com/resources/blog/how-to-install-mariadb-on-rhel8-centos8/
# run inside the container disk
$ dnf -y update
$ dnf -y install mariadb.x86_64 mariadb-common.x86_64 mariadb-devel.x86_64 mariadb-errmsg.x86_64 mariadb-server.x86_64 mariadb-server-utils.x86_64 mysql-libs.x86_64

$ vi /etc/my.cnf (according to pod)

sudo systemctl enable mariadb
sudo systemctl stop mariadb.service
echo "UPDATE mysql.user SET Password=PASSWORD('mysql')  WHERE User='root';" > input
echo "GRANT ALL ON *.* to root@'%' IDENTIFIED BY 'mysql';" >> input
echo "flush privileges;" >> input
echo "exit" >> input
sudo systemctl start mariadb.service
mysql -u root < input
sudo systemctl restart mariadb
systemctl status mariadb.service

# Make sure that /var/lib/mysql/mysql.sock file is present after the service is restarted.

Check version:
$ mysql -V

PVC check
$ systemctl status mariadb | grep Active
$ sudo dmesg -T | grep vdc
