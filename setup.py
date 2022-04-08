from setuptools import setup

setup(name='microfpga',
      version='3.1',
      description='Example module to control MicroFPGA',
      url='https://github.com/mufpga',
      author='Joran Deschamps',
      license='GPLv3',
      packages=['microfpga'],
      install_requires=[
          'pyserial',
          'serial',
          'pytest'
      ],
      zip_safe=False)
