import sys
import os
import pkg_resources
import platform

from paver.easy import task, needs, path
from paver.setuputils import setup

root_dir = path(__file__).parent.abspath()
if root_dir not in sys.path:
    sys.path.insert(0, str(root_dir))
import version


if platform.system() == 'Windows':
    install_requires = ['pywin32']


setup(name='run_exe',
      version=version.getVersion(),
      description='Run executable file, with option to try as admin on error '
      'on Windows.',
      keywords='process windows administrator launch',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='https://github.com/cfobel/run_exe',
      license='GPL',
      long_description='\n%s\n' % open('README.md', 'rt').read(),
      packages=['run_exe'],
      include_package_data=True,
      install_requires=install_requires)
