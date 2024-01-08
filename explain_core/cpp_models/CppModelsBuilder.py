from cffi import FFI
import os


def compile_modules():
    # instantiate the ffi engine
    ffibuilder = FFI()

    # define the list of c modules
    modules = ["blood_composition"]

    # get current working directory
    cwd = os.getcwd()

    # load al modules stored in the modules list
    for module in modules:
        # get the filepaths to the c and h files
        filepath_c_module = os.path.join(
            cwd, "explain_core", "cpp_models", module + ".c"
        )
        filepath_h_module = os.path.join(
            cwd, "explain_core", "cpp_models", module + ".h"
        )

        # read the header file and inject it into the ffibuilder
        with open(filepath_h_module, "r") as f:
            header = f.read()
        ffibuilder.cdef(header)

        # read the source file and inject it into the ffibuilder
        with open(filepath_c_module, "r") as f:
            source = f.read()
        ffibuilder.set_source("_" + module, source)

        # set the working directory to make sure the c compiler can find the files
        os.chdir(cwd + "/explain_core/cpp_models")

        # build the module
        output_filename = ffibuilder.compile(verbose=False)

        # remove the intermediate c and h files
        output_filename = output_filename.split(".")[0]
        intermediate_c_file = output_filename + ".c"
        intermediate_h_file = output_filename + ".h"

        if os.path.exists(intermediate_c_file):
            os.remove(intermediate_c_file)
        if os.path.exists(intermediate_h_file):
            os.remove(intermediate_h_file)

    # Change back the current working directory
    os.chdir(cwd)
