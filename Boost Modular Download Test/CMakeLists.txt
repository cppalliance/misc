cmake_minimum_required(VERSION 3.20)
project(boost_tutorial)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable vcpkg integration
if(CMAKE_TOOLCHAIN_FILE)
    message(STATUS "Using vcpkg toolchain: ${CMAKE_TOOLCHAIN_FILE}")
else()
    message(WARNING "vcpkg toolchain not specified. Use -DCMAKE_TOOLCHAIN_FILE=<vcpkg-root>/scripts/buildsystems/vcpkg.cmake")
endif()

# Find Boost components
find_package(Boost REQUIRED COMPONENTS system)

# Include directories
include_directories(${Boost_INCLUDE_DIRS})

# Executable
add_executable(${PROJECT_NAME} main.cpp)

# Link libraries
target_link_libraries(${PROJECT_NAME}
    PRIVATE
    ${Boost_LIBRARIES}
)

