# This Makefile expects that certain GNU utils are available:
# rm, cp, grep, cut, cat

HOMEPATH ?= $(HOME)
STREAMER_BASE?= ..
STREAMER_SRC := $(STREAMER_BASE)\comicstreamerlib
DIST_DIR := $(STREAMER_BASE)\windows\dist
NSIS_CMD32 :=	"C:\Program Files\NSIS\Bin\makensis.exe"
NSIS_CMD64 :=	"C:\Program Files (x86)\NSIS\Bin\makensis.exe"
VERSION := $(shell grep version "$(STREAMER_SRC)/csversion.py" | cut -d= -f2)

all: clean dist dist32 package32

x64: clean dist dist64 package64

dist:
	cd "$(STREAMER_BASE)"
	pyinstaller -w --version-file version.py -i nsis\app.ico $(STREAMER_BASE)\comicstreamer
	cp -r "$(STREAMER_SRC)\gui" $(DIST_DIR)\comicstreamer
	cp -r "$(STREAMER_SRC)\static" $(DIST_DIR)\comicstreamer
	cp mutool.exe $(DIST_DIR)\comicstreamer

dist32:
	echo "use on windows 64 bit: make x64
	cp "$(STREAMER_BASE)\comicapi\UnRAR2\UnRARDLL\unrar.dll" $(DIST_DIR)\comicstreamer
	
dist64:
	cp "$(STREAMER_BASE)\comicapi\UnRAR2\UnRARDLL\x64\unrar64.dll" $(DIST_DIR)\comicstreamer\unrar.dll
	

package32:
	echo !define RELEASE_STR $(VERSION) > $(STREAMER_BASE)\windows\nsis\release.nsh
	$(NSIS_CMD32) "$(STREAMER_BASE)\windows\nsis\comicstreamer.nsi"

package64:
	echo !define RELEASE_STR $(VERSION) > $(STREAMER_BASE)\windows\nsis\release.nsh
	$(NSIS_CMD64) "$(STREAMER_BASE)\windows\nsis\comicstreamer.nsi"

clean:
	-rm -rf dist
	-rm comicstreamer.spec
	-rm -rf build
	-rm -rf nsis/release.nsh
