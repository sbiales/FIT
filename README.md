# FIT
Fault Injection Tool: 
====================
Using Python to parse a c file and inject faults into it according to a specified probability distribution


Features
=========
1. Injects soft errors into a program (currently into the `mlp.cc` file provided)
  * looks for innermost for-loop
  * within this for-loop, it perturbs every statement that uses the `+=` operation
2. Produces an output file which it can compile and run
3. Extracts accuracy data and writes it to a `results` file

Requirements
============
1. Linux (Tested on XUbuntu 14.04)
2. g++
3. python (Tested with python3)

Getting Started
===============
Note: There are some outdated files in this directory for the purpose of learning. These files are `fit_merge.py`, `i.cc`, `test.cc`, and `test.cfg`. The `fit_merge.py` file will actually create an output file that contains the error code directly inside. This was changed in the newer version.

Without customization, this code can be run to inject errors into `mlp.cc` by running the command`python3 fit.py mlp.cfg` in terminal.

To customize this code, edit the configuration file, `mlp.cfg`. The format of the config file follows Python's `configparser` library.
Functions should be separated by spaces, and for every function there **must** be a corresponding percent. This percent refers to what percentage of the total execution time of the program is spent in the corresponding function.

`test.cc` and `test.cfg` do **not** work with `fit.py` for a specific reason. In order to obtain the accuracy results, the current design of the tool expects the original file to contain a statement resembling `printf("%d : %d\n", counter, test_size);`
Only through such a statement can the tool determine the accuracy percentage. This is something to keep in mind when trying to make the tool work for a program other than `mlp.cc`.

Future Considerations
======================
1. Accept a list of potential non-crucial functions to perturb
   * create configuration files for each possible combination of functions
   * analyze which configuration file is ideal
2. Accept multiple error rates and gather the accuracy results for each rate
3. Introduce bounds checking
4. Automate time evaluation process of determining how long is spent executing each portion of non-crucial code
5. Account for type of value to be perturbed and introduce error accordingly (currently assuming type `double`)
6. Account for a variety of function types to be perturbed (currently only looking at innermost for-loops and `+=` operations)


