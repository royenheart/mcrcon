# if you want to cross compile:
#   export PATH=$PATH:/path/to/compiler/bin
#   export CROSS_COMPILE=arm-none-linux-gnueabi-
#   make
#
# Windows cross compile:
#   i686-w64-mingw32-gcc -std=gnu99 -Wall -Wextra -Wpedantic -Os -s -o mcrcon.exe mcrcon.c -lws2_32

EXENAME = mcrcon
PREFIX ?= /usr/local

INSTALL = install
LINKER =
RM = rm -v -f -r

CC = gcc
CFLAGS = -std=gnu99 -Wall -Wextra -Wpedantic -Os -s
EXTRAFLAGS ?= -fstack-protector-strong

ifeq ($(OS), Windows_NT)
	LINKER = -lws2_32
	EXENAME = mcrcon.exe
	RM = cmd /C del /F
endif

ifeq ($(shell uname), Darwin)
	INSTALL = ginstall
	CFLAGS = -std=gnu99 -Wall -Wextra -Wpedantic -Os
endif

.PHONY: all
all: $(EXENAME)

$(EXENAME): mcrcon.c
	$(CROSS_COMPILE)$(CC) $(CFLAGS) $(EXTRAFLAGS) -o $@ $< $(LINKER)

ifneq ($(OS), Windows_NT)
.PHONY: install
install:
	$(INSTALL) -vD $(EXENAME) $(DESTDIR)$(PREFIX)/bin/$(EXENAME)
	$(INSTALL) -vD -m 0750 mcverify $(DESTDIR)$(PREFIX)/bin/mcverify
	$(INSTALL) -vD -m 0750 mcverify.py $(DESTDIR)$(PREFIX)/bin/mcverify.py
	$(INSTALL) -vD -m 0750 mcrcon.yaml $(DESTDIR)$(PREFIX)/etc/mcrcon.yaml
	$(INSTALL) -vD -m 0750 mcverify.yaml $(DESTDIR)$(PREFIX)/etc/mcverify.yaml
	$(INSTALL) -vD -m 0750 server.yaml $(DESTDIR)$(PREFIX)/etc/server.yaml
	mkdir -p $(DESTDIR)$(PREFIX)/etc/mcverifystatic
	mkdir -p $(DESTDIR)$(PREFIX)/etc/mcverifytemplates
	cp -r mcverifystatic/* $(DESTDIR)$(PREFIX)/etc/mcverifystatic/
	cp -r mcverifytemplates/* $(DESTDIR)$(PREFIX)/etc/mcverifytemplates/
	$(INSTALL) -vD -m 0644 mcrcon.1 $(DESTDIR)$(PREFIX)/share/man/man1/mcrcon.1
	mkdir -p $(DESTDIR)$(PREFIX)/var
	sed -i '/^location/c\location: $(DESTDIR)$(PREFIX)/bin' $(DESTDIR)$(PREFIX)/etc/mcrcon.yaml
	sed -i '/^export MCVERIFY_HOME/c\export MCVERIFY_HOME=$(DESTDIR)$(PREFIX)/' $(DESTDIR)$(PREFIX)/bin/mcverify
	sed -i '/^export MCVERIFY_BIN/c\export MCVERIFY_BIN=$(DESTDIR)$(PREFIX)/bin' $(DESTDIR)$(PREFIX)/bin/mcverify
	sed -i '/^export MCVERIFY_ETC/c\export MCVERIFY_ETC=$(DESTDIR)$(PREFIX)/etc' $(DESTDIR)$(PREFIX)/bin/mcverify
	sed -i '/^export MCVERIFY_VAR/c\export MCVERIFY_VAR=$(DESTDIR)$(PREFIX)/var' $(DESTDIR)$(PREFIX)/bin/mcverify
	@echo "\nmcverify installed. Run 'make uninstall' if you want to uninstall.\n"

.PHONY: uninstall
uninstall:
	$(RM) $(DESTDIR)$(PREFIX)/bin/$(EXENAME) $(DESTDIR)$(PREFIX)/bin/mcverify $(DESTDIR)$(PREFIX)/bin/mcverify.py
	$(RM) $(DESTDIR)$(PREFIX)/etc/mcrcon.yaml $(DESTDIR)$(PREFIX)/etc/mcverify.yaml $(DESTDIR)$(PREFIX)/etc/server.yaml
	$(RM) $(DESTDIR)$(PREFIX)/etc/mcverifystatic/css/style.css $(DESTDIR)$(PREFIX)/etc/mcverifystatic/public/background.png $(DESTDIR)$(PREFIX)/etc/mcverifystatic/public/favicon.ico
	$(RM) $(DESTDIR)$(PREFIX)/etc/mcverifytemplates/index.html
	$(RM) $(DESTDIR)$(PREFIX)/share/man/man1/mcrcon.1
	$(RM) $(DESTDIR)$(PREFIX)/etc/mcverifystatic $(DESTDIR)$(PREFIX)/etc/mcverifytemplates
	@echo "\nmcverify run log will still be stored in $(DESTDIR)$(PREFIX)/var/mcverify-run"
	@echo "\nmcverify uninstalled.\n"
endif

.PHONY: clean
clean:
	$(RM) $(EXENAME)
