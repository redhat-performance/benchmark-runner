
#Install Mssql 2025  https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-red-hat?view=sql-server-ver17&tabs=rhel8%2C2025rhel10
#Skip install ‘sudo yum install -y mssql-server-selinux’
#(choose: 7- Enterprise Core (PAID) - CPU Core utilization up to Operating System Maximum) - Yes/Yes/s3curePasswordString
sqlcmd -S 127.0.0.1 -U SA -P 's3curePasswordString' -C
USE master ;
GO
CREATE DATABASE tpcc ;
SELECT Name from sys.Databases
Go
SELECT Name from sys.Databases
SELECT Name from sys.tables
GO
DROP DATABASE tpcc ;
GO
SELECT @@VERSION;
GO

sudo systemctl stop mssql-server
sudo systemctl start mssql-server
sudo systemctl status mssql-server

#In case install Selinux: - need to disable it
$ vi /etc/selinux/config [Selinux turned off - Solved Permission denied]
SELINUX=disabled

$ sestatus [after reboot]
SELinux status: disabled

#Install odbc18:
Verify:
cat /etc/odbcinst.ini OR odbcinst -q -d
[ODBC Driver 18 for SQL Server]
