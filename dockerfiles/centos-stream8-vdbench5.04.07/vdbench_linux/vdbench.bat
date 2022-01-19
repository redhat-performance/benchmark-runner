
@echo off


rem
rem Copyright (c) 2000, 2013, Oracle and/or its affiliates. All rights reserved.
rem

rem
rem Author: Henk Vandenbergh.
rem


rem If the first parameter equals -SlaveJvm then this means that
rem the script must start vdbench with more memory.
rem Since all the real work is done in a slave, vdbench itself can be
rem started with just a little bit of memory, while the slaves must
rem have enough memory to handle large amount of threads and buffers.

rem Directory where this is executed from:
set dir=%~dp0

rem Set classpath.
rem %dir%                 - parent of %dir%\windows subdirectory
rem %dir%\..\classes      - for development overrides
rem %dir%\vdbench.jar     - everything, including vdbench.class

set cp=%dir%;%dir%classes;%dir%vdbench.jar

rem Proper path for java:
set java=java

rem When out of memory, modify the first set of memory parameters. See above.
rem '-client' is an option for Sun's Java. Remove if not needed.
if "%1" EQU "SlaveJvm" (
 %java% -client -Xmx512m -Xms64m -cp "%cp% " Vdb.SlaveJvm %*
) else (
 %java% -client -Xmx256m -Xms64m -cp "%cp% " Vdb.Vdbmain %*
)
