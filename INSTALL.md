Building and installing
------------------------

mcrcon's dependency is C library and POSIX getopt support. 

Compiling with GCC or CLANG:

    cc -std=gnu99 -Wpedantic -Wall -Wextra -Os -s -o mcrcon mcrcon.c
    
Note: on Windows remember to link with winsock by adding `-lws2_32` to your compiler command line.

mcverify needs flask and PyYaml python libraries, you can use pip to download:

    pip install flask
    pip install PyYaml

When you need to deploy the server, yon can use gunicorn to run the server:

    pip install gnuicorn
    gunicorn -w 1 mcverify:app

The env.yaml has been provided, you can use conda to create a new environment:

    conda env create -f env.yaml

Or you can just run "**make**":

    make           - compiles mcrcon
    make install   - installs compiled binaries, python and bash files, configuration files, static and templates folder, manpage to the system
    make uninstall - removes downloaded softwares from the system
    
    file install locations:
        /usr/local/bin/mcrcon
        /usr/local/bin/mcverify
        /usr/local/bin/mcverify.py
        /usr/local/etc/mcverify.yaml
        /usr/local/etc/mcrcon.yaml
        /usr/local/etc/server.yaml
        /usr/local/etc/mcverifystatic/
        /usr/local/etc/mcverifytemplates/
        /usr/local/share/man/man1/mcrcon.1
    Run folder will be created:
        /usr/local/var/
    Log folder will be created when mcverify run:
        /usr/local/var/mcverify

Makefile "**install**" and "**uninstall**" rules are disabled on windows.
