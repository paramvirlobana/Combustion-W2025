import numpy as np
import cantera as ct


def main():
    print("this is the start of the program")
    gas1 = ct.Solution('gri30.yaml')

    gas1()

if __name__ == "__main__":
    main()
