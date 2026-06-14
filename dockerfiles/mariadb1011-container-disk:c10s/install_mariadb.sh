#Pod Image: quay.io/sclorg/mariadb-1011-c10s
#Code: https://github.com/sclorg/mariadb-container
#https://reintech.io/blog/install-mysql-centos-9

#VM Image:
dnf -y update
centos9
sudo dnf config-manager --set-enabled crb
dnf -y install mariadb.x86_64 mariadb-common.x86_64 mariadb-errmsg.x86_64 mariadb-server.x86_64 mariadb-server-utils.x86_64 mysql-libs.x86_64
Centos10
dnf -y install mariadb mariadb-server mariadb-server-utils
dnf install -y https://dev.mysql.com/get/mysql80-community-release-el9-5.noarch.rpm && \
dnf install -y mysql-community-libs --nogpgcheck && \
ln -sf /usr/lib64/mysql/libmysqlclient.so.21 /usr/lib64/libmysqlclient.so.21 && \
dnf clean all


systemctl status mariadb
sudo systemctl start mariadb
pip install --upgrade oauthlib cloud-init requests-oauthlib [benchmark-operator]
mysql -V
