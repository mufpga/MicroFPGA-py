from setuptools import setup

setup(name='microfpga',
      version='1.0',
      description='Example module to control MicroFPGA',
      url='https://github.com/mufpga',
      author='Joran Deschamps',
      license='GPLv3',
      packages=['microfpga'],
      install_requires=[
          'serial',
          'pyserial'
      ],
      zip_safe=False)