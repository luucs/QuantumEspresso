#!/bin/bash

file="licoo2_base"
in_out="licoo2"

echo "Enter 1 for the ecutwfc, 2 for kpoints tests, 3 for both:"
read -e part


if [ "$part" -eq 1 ] || [ "$part" -eq 3 ]; then
    echo "Ecutwfc conv tests..."
    cp $file ecutwfc && cd ecutwfc
    sed -i 's/<K1>/8/g' $file # safe k mesh
    sed -i 's/<K2>/8/g' $file

    for i in {20..120..20}; do
        ecutrho=$(echo "${i}*12" | bc -l) # define dual
        sed "s/<ecutwfc>/${i}/" $file > tmp.in
        sed "s/<ecutrho>/${ecutrho}/" tmp.in > ${in_out}_${i}.in
        rm -rf tmp.in
        echo "Running pw.x for ecutwfc ${i} Ry"
        mpirun -np 8 pw.x -in ${in_out}_${i}.in > ${in_out}_${i}.out
    done
    echo "Ecutwfc tests finished, running totendiffs..."
    /home/lucas/Desktop/scripts/toten_diffs.sh 
    echo "Showing diff_ev..."
    cat diff_ev
    echo "Run part 2 for k mesh"
elif [ "$part" -eq 2 ]; then
    echo "Choose a reasonable ecutwfc for kpoint convergence:"
    read -e ecut
    ecut2=$(echo "${ecut}*12" | bc -l)
    echo "Starting k mesh checkings..."
    cp $file kpoints && cd kpoints
    sed -i "s/<ecutwfc>/${ecut}/g" $file
    sed -i "s/<ecutrho>/${ecut2}/g" $file

    for j in {2..20..2}; do
        j2=$(echo "${j}*2" | bc -l)
        sed "s/<K1>/${j}/g" $file > tmp.in
        sed "s/<K2>/${j}/g" tmp.in > ${in_out}_k${j}.in
        mpirun -np 8 pw.x -in ${in_out}_k${j}.in > ${in_out}_k${j}.out
    done
elif [ "$part" -eq 3 ]; then
    echo "Running automatically k point sampling, choosing large ecutwfc..."
    ecut=90
    ecut2=$(echo "${ecut}*12" | bc -l)
    echo "Starting k mesh checkings..."
    cp $file kpoints && cd kpoints
    sed -i "s/<ecutwfc>/${ecut}/g" $file
    sed -i "s/<ecutrho>/${ecut2}/g" $file

    for j in {2..20..2}; do
        j2=$(echo "${j}*2" | bc -l)
        sed "s/<K1>/${j}/g" $file > tmp.in
        sed "s/<K2>/${j}/g" tmp.in > ${in_out}_k${j}.in
        mpirun -np 8 pw.x -in ${in_out}_k${j}.in > ${in_out}_k${j}.out
    done
else
    echo "Invalid input. Please enter 1, 2 or 3."
fi