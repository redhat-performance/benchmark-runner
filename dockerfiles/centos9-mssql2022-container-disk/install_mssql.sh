wget https://cloud.centos.org/centos/9-stream/x86_64/images/CentOS-Stream-GenericCloud-x86_64-9-20240527.0.x86_64.qco
https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-red-hat?view=sql-server-ver16&tabs=rhel9%2C2025rhel9
# run inside the container disk
$ dnf -y update
(choose: 7- Enterprise Core (PAID) - CPU Core utilization up to Operating System Maximum)
sqlcmd -S 127.0.0.1 -U SA -P 's3curePasswordString'
USE master ;
GO
DROP DATABASE tpcc ;
GO
CREATE DATABASE tpcc
SELECT Name from sys.Databases
Go
SELECT Name from sys.Databases
SELECT Name from sys.tables
 /var/opt/mssql/mssql.conf (memory.memorylimitmb = 8192MB) - Not necessary because MSSQL sets the size automatically.

$ sudo systemctl stop mssql-server
$ sudo systemctl start mssql-server
$ sudo systemctl status mssql-server


In case install Selinux: - need to disable it
$ vi /etc/selinux/config [Selinux turned off - Solved Permission denied]
SELINUX=disabled

$ sestatus [after reboot]
SELinux status: disabled

Install odbc17:
https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=redhat18-install%2Credhat17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline#17

#RHEL 9
curl https://packages.microsoft.com/config/rhel/9/prod.repo | sudo tee /etc/yum.repos.d/mssql-release.repo

sudo yum remove unixODBC-utf16 unixODBC-utf16-devel #to avoid conflicts
sudo ACCEPT_EULA=Y yum install -y msodbcsql17
# optional: for bcp and sqlcmd
sudo ACCEPT_EULA=Y yum install -y mssql-tools
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc
# optional: for unixODBC development headers
sudo yum install -y unixODBC-devel


Verify:
cat /etc/odbcinst.ini
[ODBC Driver 17 for SQL Server]
