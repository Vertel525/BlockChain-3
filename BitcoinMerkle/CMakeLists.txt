cmake_minimum_required(VERSION 3.13)
project(BitcoinMerkle CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBBITCOIN REQUIRED libbitcoin-system)

# Bitcoin Merkle medzio programa
add_executable(bitcoin_merkle main.cpp merkle.cpp)
target_include_directories(bitcoin_merkle PRIVATE ${LIBBITCOIN_INCLUDE_DIRS})
target_link_directories(bitcoin_merkle PRIVATE ${LIBBITCOIN_LIBRARY_DIRS})
target_link_libraries(bitcoin_merkle PRIVATE ${LIBBITCOIN_LIBRARIES})
target_compile_options(bitcoin_merkle PRIVATE ${LIBBITCOIN_CFLAGS_OTHER})

# Atskiru hash rezimu demonstracija
add_executable(hash_modes hash_modes.cpp)
target_include_directories(hash_modes PRIVATE ${LIBBITCOIN_INCLUDE_DIRS})
target_link_directories(hash_modes PRIVATE ${LIBBITCOIN_LIBRARY_DIRS})
target_link_libraries(hash_modes PRIVATE ${LIBBITCOIN_LIBRARIES})
target_compile_options(hash_modes PRIVATE ${LIBBITCOIN_CFLAGS_OTHER})
