import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def printHead() -> None:
    head="""           
            .                                                 
    Combustion | Rich-Quenck-Burn |
    ------                      .       
    PROGRAMMED FOR COMBUSTION WINTER 2025                          .
            .                 .                               .                            
                        
    """
    print(head)

def plot(df: pd.DataFrame, x: str, y: str, show: bool = False):
    sns.scatterplot(data=df, x=x, y=y)
    plt.title(f"{y} vs {x}")
    if show:
        plt.show()

def make_dir(DIR:str) -> None:
    try:
        os.mkdir(DIR)
        print(f"Directory '{DIR}' created successfully.")
    except FileExistsError:
        print(f"Directory '{DIR}' already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")