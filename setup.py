from sys import version_info
from setuptools import setup

if version_info.major == 3 and version_info.minor < 6 or \
        version_info.major < 3:
    print('Your Python interpreter must be 3.6 or greater!')
    exit(1)


setup(name='cdpnotify',
      version='0.0.1',
      description='MakerDAO CDP Collateralization Notification Bot',
      url='https://github.com/gcarq/cdpnotify',
      author='gcarq',
      author_email='michael.egger@tsn.at',
      license='GPLv3',
      packages=['cdpnotify'],
      install_requires=[
          'SQLAlchemy',
          'python-telegram-bot',
          'web3',
      ],
      include_package_data=True,
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'cdpnotify = cdpnotify.__main__:main'
          ]
      },
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Office/Business :: Financial :: Investment',
          'Intended Audience :: Science/Research',
      ])
