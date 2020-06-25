from setuptools import setup
from distutils import log
from setuptools.command.install import install
from setuptools.command.install_scripts import install_scripts
import os, stat

class OverrideInstall(install):
    def run(self):
        uid, gid = 0,0
        mode = stat.S_IRWXO
        install.run(self)
        for filepath in self.get_outputs():
            log.info("Overriding setuptools mode of scripts ...")
            log.info("Changing ownership of %s to uid: %s gid: %s" %
                     (filepath, uid, gid))
            os.chown(filepath, uid, gid)
            log.info("Changing permission of %s to %s" %
                     (filepath, oct(mode)))
            os.chmod(filepath, mode)

with open("README.md", mode='r') as f:
    long_description = f.read()

setup(
    name='fb_feed_sync',
    version='1.0',
    description='Synchronize data to a google sheet from a plenty export',
    license='GPLv3',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Sebastian Fricke',
    author_email='sebastian.fricke.linux@gmail.com',
    packages= ['fb_feed_sync', 'fb_feed_sync.packages'],
    install_requires=['configparser', 'argparse', 'pandas', 'numpy',
                      'google-api-python-client',
                      'google-auth-httplib2', 'google-auth-oauthlib',
                      'google-auth'],
    url='https://github.com/initBasti/fb_feed_sync',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Topic :: Utilities"
    ],
    entry_points={'script':['fb_feed_sync = fb_feed_sync.__main__:main']},
    data_files=[('data', ['data/.credentials.json', 'data/config.ini'])],
    include_pacakage_data = True,
    cmdclass={'install':OverrideInstall}
)
