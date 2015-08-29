from distutils.core import setup
import py2exe, os, shutil
from modulefinder import Module


wd_base = 'C:\\Python27\\Lib\\site-packages\\selenium\\webdriver'
RequiredDataFiles = [('selenium/webdriver/firefox', ['%s\\firefox\\webdriver.xpi'%(wd_base), '%s\\firefox\\webdriver_prefs.json'%(wd_base)])]

setup(console=['drlv.py'],
      data_files= RequiredDataFiles,
      name = "Drlv automatic mail sender",
      version = "0.7",
      author = "Janis Mateuss",
      author_email = 'jajanka3@gmail.com',
      license = "Janis Mateuss",
      # copyright = "Copyright (c) 2014 Janis Mateuss.",
      options={
        "py2exe":{
                "skip_archive": True,
                "unbuffered": True,
                "optimize": 2,
          }
        }
      )

# Remove the build tree
REMOVE_BUILD_ON_EXIT = True
if REMOVE_BUILD_ON_EXIT:
     shutil.rmtree('build/')
