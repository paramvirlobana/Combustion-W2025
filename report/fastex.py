import os
import sys
import platform
import subprocess

if platform.system() == "Windows":
    __LATEXPDF = os.path.join(os.getenv('LOCALAPPDATA'), r'Programs\MiKTeX\miktex\bin\x64\pdflatex.exe')
    __LATEXBIB = os.path.join(os.getenv('LOCALAPPDATA'), r'Programs\MiKTeX\miktex\bin\x64\bibtex.exe')
elif platform.system() == "Linux":
    sys.exit(f"{platform.system()} systems not supported yet. Exiting.")
else:
    sys.exit(f"{platform.system()} is not a supported operating system name. Exiting.")

def perf_graphs(tex_file:str):
    try:
        latex_compiler(tex_file)
    except Exception as ex:
        print(f"Compilation failed: {ex}")

def remove_temp_files(tex_file:str):
    base_name, _ = os.path.splitext(tex_file)
    file_extensions = [
        ".aux", ".bbl", ".blg", ".lof", 
        ".log", ".lot", ".toc", ".spl",
        ".out"
    ]
    
    for ext in file_extensions:
        file_to_remove = base_name + ext
        if os.path.isfile(file_to_remove):
            try:
                os.remove(file_to_remove)
                print(f"Removed {file_to_remove}")
            except OSError as e:
                print(f"Could not remove {file_to_remove}: {e}")

def latex_compiler(tex_file: str):
    """
    This function compiles the LaTeX file

    """
    
    if not os.path.isfile(__LATEXPDF):
        raise FileNotFoundError(f"pdflatex not found at '{__LATEXPDF}'")
    if not os.path.isfile(__LATEXBIB):
        raise FileNotFoundError(f"bibtex not found at '{__LATEXBIB}'")

    if not os.path.isfile(tex_file):
        raise FileNotFoundError(f"Cannot find '{tex_file}'")

    pdflatex_command = [
        __LATEXPDF,
        "-shell-escape",
        "-interaction=nonstopmode",
        "-halt-on-error",
        tex_file
    ]

    bibtex_command = [
        __LATEXBIB,
        os.path.splitext(os.path.basename(tex_file))[0]
    ]
    
    try:
        subprocess.run(pdflatex_command, check=True)
        subprocess.run(bibtex_command, check=True)
        subprocess.run(pdflatex_command, check=True)
        subprocess.run(pdflatex_command, check=True)
        
        print(f"Successfully compiled {tex_file}")

        remove_temp_files(tex_file)
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while compiling {tex_file}: {e}")
        raise

if __name__ == "__main__":
    try:
        perf_graphs("main.tex")
    except:
        print('failed')

