#include <boost/asio.hpp>
#include <iostream>
#include <chrono>

int main() {
    boost::asio::io_context io;

    // Create a timer that expires after 2 seconds
    boost::asio::steady_timer timer(io, std::chrono::seconds(2));

    std::cout << "Starting timer...\n";

    // Set up an asynchronous wait
    timer.async_wait([](const boost::system::error_code& ec) {
        if (!ec) {
            std::cout << "Timer expired! Hello from Boost.Asio!\n";
        } else {
            std::cerr << "Timer error: " << ec.message() << "\n";
        }
    });

    std::cout << "Waiting for timer...\n";

    // Run the io_context to execute the async operation
    io.run();

    std::cout << "Done!\n";
    return 0;
}

