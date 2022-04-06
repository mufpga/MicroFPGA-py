<a href="https://mufpga.github.io/"><img src="https://raw.githubusercontent.com/mufpga/mufpga.github.io/main/img/logo_title.png" alt="Overview"/>

</a>

![version](https://img.shields.io/badge/version-3.1-blue)



# Overview

MicroFPGA is an FPGA-based platform for the electronic control of microscopes. It aims at using affordable FPGA to generate or read signals from a variety of devices, including cameras, lasers, servomotors, filter-wheels, etc. It can be controlled via [Micro-Manager](https://micro-manager.org/MicroFPGA), or its [Java](https://github.com/mufpga/MicroFPGA-java), [Python](https://github.com/mufpga/MicroFPGA-py) and [LabView](https://github.com/mufpga/MicroFPGA-labview) communication libraries, and comes with optional complementary [electronics](https://github.com/mufpga/MicroFPGA-electronics).

Documentation and tutorials are available on [https://mufpga.github.io/](https://mufpga.github.io/).



<img src="https://raw.githubusercontent.com/mufpga/mufpga.github.io/main/img/figs/G_overview.png" alt="Overview"/>

## Content

This repository contains the Python package to control MicroFPGA. To use `microfpga` in you Python environment, you can directly install it from PyPi using the following command:

```bash
pip install microfpga
```

Alternatively, you can install it from the source code in a minimal environment:

``` bash
conda env create -f environment.yml
conda activate microfpga
pip install -e .
```

The package contains examples on how to use MicroFPGA.

<!---

## Cite us

Deschamps J, Kieser C, Hoess P, Deguchi T and Ries J, 

--->

MicroFPGA was written by Joran Deschamps, EMBL (2020).

