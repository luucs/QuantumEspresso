# script that takes vc relax calculation and generates POSCAR file
import subprocess
import numpy as np
import sys

bohr_to_angs=0.529177

def remove_empty(lista):
    clean = list(filter(lambda x: x != '',lista.split(" ")))
    return clean

def count_atoms(atomic_positions):
    atom_dict = {}
    for line in atomic_positions:
        atom = line.split(" ")[0]
        if atom in atom_dict:
            atom_dict[atom] += 1
        else:
            atom_dict[atom] = 1
    return atom_dict 

def extract_alat(s):
    words = s.split()
    number = words[-1][:-1] # remove last trailing parenthesis
    return float(number)*bohr_to_angs

def grep_in_file(pattern, filename):
    try:
        output = subprocess.check_output(["grep", "-A 13", pattern, filename])
        process_grep(output=output.decode("utf-8"))
#        return output.decode("utf-8")
    except subprocess.CalledProcessError:
        return ""
    
def process_grep(output):
    lines = output.split('\n')
    #print(lines)
    for i in range(len(lines)):
        if "CELL_PARAMETERS" in lines[i]:
           # print(lines[i+1].split(" "))
            vec1 = [float(line) for line in remove_empty(lines[i+1])]
            vec2 = [float(line) for line in remove_empty(lines[i+2])]
            vec3 = [float(line) for line in remove_empty(lines[i+3])]
            alat = extract_alat(lines[i])
            lattice_vectors = np.array([vec1,vec2,vec3])
            scaled_vectors = alat*lattice_vectors
        if "ATOMIC_POSITIONS (crystal)" in lines[i]:
            atomic_positions = list(lines[i+1:-1])
           # print(atomic_positions)
         #   print(atomic_positions)
   # print(type(atomic_positions))
    generate_poscar(scaled_vectors,atomic_positions)

def generate_poscar(scaled_vectors,atomic_positions):
    write_string = "POSCAR generated from QE output file \n"
    write_string += "1.0" # scaling factor
    write_string += "\n"
    for row in scaled_vectors:
        for value in row:
            write_string += f"        {value:.10f}          "
        write_string += "\n"
    atom_dict =  count_atoms(atomic_positions=atomic_positions)
    for atom in atom_dict.keys():
        write_string += f"   {atom}   "
    write_string += "\n"
    for _,value in atom_dict.items():
        write_string += f"  {value}  "
    write_string += "\n"
    write_string += "Direct"
    write_string += "\n"
    for line in atomic_positions:
        processed_line = line.split(' ')
        processed_line = [item for item in processed_line if item not in atom_dict.keys()]    
        write_string += ' '.join(processed_line)
        write_string += "\n"
    with open("POSCAR",'w') as f:
        f.write(write_string)

def main():
    if len(sys.argv) < 2:
        print("wrong # arg")
        return
    grep_in_file("Begin final coordinates",sys.argv[1])
    
if __name__ == '__main__':
    main()    








