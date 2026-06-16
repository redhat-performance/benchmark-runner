#Pod image: quay.io/sclorg/postgresql-16-c10s
#Code: https://github.com/sclorg/postgresql-container
#https://linuxize.com/post/how-to-install-postgresql-on-centos-8/

#VM image:
sudo dnf -y update
sudo dnf config-manager --set-enabled crb
dnf -y install postgresql.x86_64 postgresql-contrib.x86_64 postgresql-server.x86_64 postgresql-libs

sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl status postgresql
sudo systemctl stop postgresql
sudo systemctl enable postgresql
postgres -V
