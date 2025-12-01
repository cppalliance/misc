# Boost.Asio Tutorial

A minimal C++ project demonstrating Boost.Asio usage with vcpkg.

## Prerequisites

- CMake 3.20 or higher
- C++17 compatible compiler

## Building

0. Install `vcpkg` from source.

```bash
git clone https://github.com/microsoft/vcpkg.git ~/vcpkg
~/vcpkg/bootstrap-vcpkg.sh
```

1. Configure the project with CMake, pointing to your vcpkg toolchain:

```bash
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE=~/vcpkg/scripts/buildsystems/vcpkg.cmake
```

2. Build the project:

```bash
cmake --build build
```

3. Run the executable:

```bash
./build/boost_tutorial
```

## What it does

This project demonstrates a simple asynchronous timer using Boost.Asio. The program:
- Creates an `io_context` for asynchronous operations
- Sets up a timer that expires after 2 seconds
- Uses `async_wait` to handle the timer expiration asynchronously
- Runs the `io_context` to execute the async operation

## Notes

- vcpkg will automatically download and build Boost.Asio (and its dependencies) during the CMake configuration step
- The `vcpkg.json` manifest file specifies Boost.Asio as a dependency

