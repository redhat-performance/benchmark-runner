USE master;
GO
IF DB_ID('tpcc') IS NOT NULL
BEGIN
    ALTER DATABASE tpcc SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE tpcc;
END
GO
CREATE DATABASE tpcc
ON PRIMARY
(  NAME       = MSSQL_data_1,
   FILENAME   = 'd:\mssql\data\tpcc.mdf',
   SIZE       = 49152MB,
   FILEGROWTH = 20)
LOG ON
(  NAME       = MSSQL_data_log,
   FILENAME   = 'd:\mssql\data\tpcc_log.mdf',
   SIZE       = 20480MB,
   FILEGROWTH = 500MB,
   MAXSIZE    = 27000MB)
go
