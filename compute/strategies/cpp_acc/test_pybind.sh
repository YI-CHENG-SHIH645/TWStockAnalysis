cd ../core/build || exit
make clean
rm CMakeCache.txt
cmake ..
make
cd ../../compute || exit
python -m strategies.cpp_acc.test_pybind
cd ../core/build || exit
make clean
