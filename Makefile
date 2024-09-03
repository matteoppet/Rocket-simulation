# Compiler to use
CC = gcc

# Directories
SRC_DIR = src
SRC_DIR_C_FILES = src/c_scripts
LIB_DIR = lib

# Source files and corresponding DLL names (in the subdirectory)
SRC_FILES = $(SRC_DIR_C_FILES)/rocket_physics.c
DLL_FILES = $(LIB_DIR)/physics.dll

# Python script to run (in the subdirectory)
PYTHON_SCRIPT = $(SRC_DIR)/main.py

# Compiler flags to create a shared library
CFLAGS = -shared -fPIC -o

# Default target: Compile all DLLs and run the Python script
all: $(DLL_FILES) run

# Only compile the DLL if it doesn't exist
$(DLL_FILES): $(SRC_FILES)
	@if [ ! -f $@ ]; then \
		echo "Compiling $@ because it doesn't exist."; \
		@mkdir -p $(LIB_DIR); \
		$(CC) $(SRC_FILES) $(CFLAGS) $(DLL_FILES); \
	fi

# Run the Python script
run: $(DLL_FILES)
	python $(PYTHON_SCRIPT)

# Clean up compiled files
clean:
	rm -f $(DLL_FILES)

.PHONY: all run clean