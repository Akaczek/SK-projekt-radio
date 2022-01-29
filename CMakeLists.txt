cmake_minimum_required(VERSION 3.10)
project(Radio)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR})
set(CMAKE_CXX_FLAGS -pthread)

add_executable(Radio serwer.cpp)

add_compile_options(-Wall -Wextra --std=c++20 -pthread)

