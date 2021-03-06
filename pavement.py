from paver.easy import *
from paver.setuputils import setup
import urllib
import os

setup(
    name="ComicStreamer",
    packages=[],
    version="1.0",
    url="https://github.com/Tristan79/ComicStreamer",
    author="Beville/Davide Romanini/Tristan Crispijn",
    author_email="tristan@monkeycat.nl"
)

@task
def libunrar():
    UNRAR_SRC = "http://www.rarlab.com/rar/unrarsrc-5.3.2.tar.gz"
    dest = "libunrar/" + os.path.basename(UNRAR_SRC)
    if not os.path.exists(dest):
        print "Fetching " + UNRAR_SRC + "..."        
        urllib.urlretrieve(UNRAR_SRC, dest)
    if not os.path.exists("libunrar/unrar"):
        print "Unpacking " + dest + "..."
        sh("tar xfz %s -C libunrar" % (dest))
    print "Compiling unrar..."    
    sh("cd libunrar/unrar && make lib")
    sh("cp libunrar/unrar/libunrar.so libunrar/libunrar.so")
        
    
    
@task
@needs(["distutils.command.sdist"])
def sdist():
    """Generate docs and source distribution."""
    pass
