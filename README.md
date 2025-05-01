# Combustion-W2025

Author: ```Paramvir Lobana``` \
Program written for the course: ```Combustion``` ```Winter 2025``` ```Concordia University, Montreal```

## Description
Cantera model for an RQL combustor using ammonia as the fuel. For the complete report, see [FinalReport](report/main.pdf)

## Usage

The program can be used using the command line. Following arguments are available:

```bash
usage: RQL Reactor [-h] [-p] [-s] [-r] [-d]

Simulation for the reaction mechanism for an RQL combustor.

options:
  -h, --help       show this help message and exit
  -p, --primary    Runs initial calculations for the primary region.
  -s, --secondary  Runs initial calculations for the secondary air region.
  -r, --rql        Runs the RQL combustor routine.
  -d, --data       Save all output data to csv.
```
