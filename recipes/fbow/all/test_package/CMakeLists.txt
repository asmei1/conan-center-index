cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(fbow REQUIRED)
find_package(OpenMP REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE
    fbow::fbow
    OpenMP::OpenMP_CXX)
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED TRUE
)
