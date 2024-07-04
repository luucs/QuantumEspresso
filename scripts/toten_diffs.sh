#!/bin/bash

echo "Enter the file extension (e.g., .out, .pwo):"
read -e ext
echo "-------"

if [[ $ext != .* ]]; then
    ext=".$ext"
fi

if ! ls *"$ext" > /dev/null 2>&1; then
    echo "No files with extension $ext found."
    exit 1
fi

grep "!" *"$ext" | sort -t= -k2nr > energy_all

echo "Check if files are ordered in 'energy_all':"
cat energy_all

echo "Write the name of the file if they are:"
read -e ext1

if [[ ! -f $ext1 ]]; then
    echo "File $ext1 does not exist."
    exit 1
fi

awk '{print $5}' "$ext1" > energy

last_value=$(tail -n 1 energy)
awk -v last="$last_value" '{ diff = $1 - last; print diff }' energy > diff
awk '{print $1 * 13.60570}' diff > diff_ev

# Prepare the stress values with the filename and pressure
> tstress
for file in *"$ext"; do
    P_values=$(grep "P=" "$file" | awk '{print $NF}')
    if [[ -n $P_values ]]; then
        echo "$file, $P_values" >> tstress
    fi
done

