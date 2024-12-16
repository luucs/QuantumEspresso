import sys
import pandas as pd

bohr_to_angs = 0.529177

def get_last_cell_parameters(filename):
    with open(filename, 'r') as file:
        content = file.readlines()

    vecs = []
    rows = []
    read_section = False

    for i, line in enumerate(content):
        # Detect the start of the final geometry
        if "Begin final coordinates" in line:
            read_section = True
            vecs = []  # Reset vecs for the new section
            rows = []  # Reset rows for the new section
            continue
        elif "End final coordinates" in line:
            read_section = False
            break 

        if read_section:
            if "CELL_PARAMETERS (angstrom)" in line:
                vecs = [
                    [float(x) for x in content[i + 1].split()],
                    [float(x) for x in content[i + 2].split()],
                    [float(x) for x in content[i + 3].split()]
                ]
                continue
            if "ATOMIC_POSITIONS (angstrom)" in line:
                for pos_line in content[i + 1:]:
                    if pos_line.strip() == "" or "End final coordinates" in pos_line:
                        break
                    parts = pos_line.split()
                    if len(parts) == 4:
                        rows.append({
                            'atom': parts[0],
                            'x': float(parts[1]),
                            'y': float(parts[2]),
                            'z': float(parts[3])
                        })
    atom_df = pd.DataFrame(rows)
    return vecs, atom_df



def generate_poscar(vecs, atom_df):
    write_string = f"Generated from QE - {sys.argv[1]} vc relax \n"
    write_string += "1.0\n"  # scaling factor
    for row in vecs:
        write_string += "   ".join(f"{value:.10f}" for value in row) + "\n"
    
    unique_atoms = set(i for i in atom_df['atom'])
    print(unique_atoms)
    write_string += "   ".join(unique_atoms) + "\n"
    counts = [len(atom_df.query(f" atom == '{i}' ")) for i in unique_atoms]
    print(counts)
    for i in counts:
        write_string += str(i) + " "
    write_string += "\n"        
    
    write_string += "Cartesian\n" # if "crystal" coords, then Direct
    for atom in unique_atoms:
        unique = atom_df.query(f"atom == '{atom}'")
        for _, row in unique.iterrows():
            write_string += "   ".join(f"{row[col]:.10f}" for col in ['x', 'y', 'z']) + "\n"

    with open("POSCAR", 'w') as f:
        f.write(write_string)

def main():
    if len(sys.argv) < 2:
        print("Error: Please provide the output file as an argument.")
        return
    
    scaled_vectors, atomic_positions = get_last_cell_parameters(sys.argv[1])
    
    if scaled_vectors is not None and atomic_positions is not None:
        generate_poscar(scaled_vectors, atomic_positions)
        print("POSCAR file generated successfully.")
    else:
        print("Error: Couldn't process the output file.")

if __name__ == '__main__':
    main()

