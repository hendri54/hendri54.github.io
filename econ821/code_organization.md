{{econ821_header.txt}}

# Organizing our code

## Directory structure

Course home directory (e.g. `~/documents/econ821`)

* `shared`: code for general purpose functions
	* put on the matlab path by `go_econ821`
	* contains a function that returns constants shared by all projects: `const_821.m`
	* [`shared` code as zip file](shared.zip)
* `projectX`: code for each project
	* `mat`: matrix files `.mat`
	* `out`: output files, such as figures, tables

## Project code

Suffix each file with a project name, such as `_olg`.
This ensures unique names.

`const_olg`: defines all constants for a project

* model parameters
* directories
* figure formatting
* etc

-----------