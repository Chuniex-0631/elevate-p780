cmake_minimum_required(VERSION 3.22.1)
project(p780_sendfile_probe C)

add_library(sendfile_probe SHARED sendfile_probe.c)
target_compile_options(sendfile_probe PRIVATE -Wall -Wextra -Werror)
