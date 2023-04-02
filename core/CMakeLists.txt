cmake_minimum_required(VERSION 3.18)
project(core)
set(CMAKE_CXX_STANDARD 17)

find_package(pybind11 CONFIG REQUIRED)
find_package(GTest REQUIRED)
list(APPEND third_party
    pybind11::module
    OpenMP::OpenMP_CXX
)

if (APPLE)
    # Require CMake 3.16+ on Mac OSX, as previous versions of CMake had trouble locating
    # OpenMP on Mac. See https://github.com/dmlc/xgboost/pull/5146#issuecomment-568312706
    cmake_minimum_required(VERSION 3.16)
    find_package(OpenMP)
    if (NOT OpenMP_FOUND)
        # Try again with extra path info; required for libomp 15+ from Homebrew
        execute_process(COMMAND brew --prefix libomp
          OUTPUT_VARIABLE HOMEBREW_LIBOMP_PREFIX
          OUTPUT_STRIP_TRAILING_WHITESPACE)
        #    set(CMAKE_C_COMPILER "/opt/homebrew/opt/llvm/bin/clang")
        #    set(CMAKE_CXX_COMPILER "/opt/homebrew/opt/llvm/bin/clang++")
        set(OpenMP_C_FLAGS
          "-Xpreprocessor -fopenmp -I${HOMEBREW_LIBOMP_PREFIX}/include")
        set(OpenMP_CXX_FLAGS
          "-Xpreprocessor -fopenmp -I${HOMEBREW_LIBOMP_PREFIX}/include")
        set(OpenMP_C_LIB_NAMES omp)
        set(OpenMP_CXX_LIB_NAMES omp)
        set(OpenMP_omp_LIBRARY ${HOMEBREW_LIBOMP_PREFIX}/lib/libomp.dylib)
        find_package(OpenMP REQUIRED)
    endif ()
else ()
    find_package(OpenMP REQUIRED)
endif ()


add_subdirectory(src)
