#  Copyright (c) 2023. Harvard University
#
#  Developed by Research Software Engineering,
#  Harvard University Research Computing
#  and The Harvard T.H. Chan School of Public Health
#  Authors: Michael A Bouzinier, Kezia Irene, Michelle Audirac
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#


"""
See:

https://unidata.github.io/netcdf4-python/
https://neetinayak.medium.com/combine-many-netcdf-files-into-a-single-file-with-python-469ba476fc14
https://docs.xarray.dev/en/stable/api.html

"""
import argparse
import logging
from typing import Optional, List

from netCDF4 import Dataset

#from nsaph import init_logging


class NetCDFDataset:
    """
    Class to combine NetCDF dataset with absolute values with
    dependent datasets containing components
    """
    def __init__(self):
        self.dataset: Optional[Dataset] = None
        self.main_var: Optional[str] = None
        '''The name of the main variable'''
        self.components_list = [] 
        self.percentages: List[str] = []
        '''The names of the component variables containing percentages'''
        self.abs_values: List[str] = []
        '''The names of the component variables containing absolute values'''
        self.absolute_values_read = False 
        
        return
    
    def create_new_dataset(self, datasett, outfile): 
        print("create_new_dataset: Create new netcdf file with name: ", outfile)
        # Create a new netCDF file (need to create new file to not modify the absolute file)
        # Output file
        dsout = Dataset(outfile, "w", format="NETCDF4_CLASSIC")

        # Copy dimensions
        for dname, the_dim in datasett.dimensions.items():
            print(dname, len(the_dim))
            dsout.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)

        # Copy variables
        for v_name, varin in datasett.variables.items():
            outVar = dsout.createVariable(v_name, varin.datatype, varin.dimensions)
            print(varin.datatype)

            # Copy variable attributes
            outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})

            outVar[:] = varin[:]
        print("finish creating new netcdf file")
        return dsout

        
    def read_abs_values(self, filename: str, outfile, var: str = None):
        """
        Reads the NetCDF dataset from a *.nc file
        Assumes that this dataset contains absolute values of
        the variable with the name provided by var parameter.

        Raises an exception if the variable is not None but is not present n the dataset.
        If the parameter "var" is None, checks that there is only one variable present beside "lat" and "lon".
        Raises exception if there is more than one variable

        :param var: The variable containing the absolute values of the feature of interest, e.g., "pm25"
            If None, defaults to a single variable present in teh dataset beside "lat" and "lon"
        :param filename: A path to file to read.
            Can also be a python 3 pathlib instance or the URL of an OpenDAP dataset.
        :raises: ValueError if var is None and there is more than one variable in the dataset or, if var
            is not None and is not present in teh dataset
        """
        # Create a Dataset variable for the file
        datasett = Dataset(filename)

        # If var is None, check that there is only one variable present beside "lat" and "lon"
        if var is None:
            variables = list(datasett.variables.keys())
            variables.remove("LAT")
            variables.remove("LON")
            if len(variables) != 1:
                raise ValueError("If var is None, there must be exactly one variable besides 'lat' and 'lon'.")

            # Get the variable name
            var = variables[0]
            
        # Create new netcdf file  
        self.dataset = self.create_new_dataset(datasett,outfile)
        
        # Check that the specified variable is present in the dataset
        if var not in self.dataset.variables:
            raise ValueError("The variable '%s' is not present in the dataset." % var)

        # Get the absolute values of the specified variable
        self.abs_values = self.dataset.variables[var][:]

        # Assign the units from the old dataset to the new dataset
        self.dataset.variables[var].units = datasett.variables[var].units
        self.absolute_values_read = True
        self.main_var = var 
        print("Done with read_abs_values")
        return var

    def add_component(self, filename: str, var: str = None, abs_var: str = None):
        """
        Reads the NetCDF dataset from a *.nc file
        Assumes that this dataset contains percentage of a component defined by
        the var parameter.

        Can only be called after the dataset is initialized with absolute values.

        :param var: The variable containing percentage of a certain component
        :param abs_var: The variable name to contain absolute values of the component. If omitted,
            it is constructed from the percentage variable name either by removing 'p' if the
            variable starts with 'p' otherwise, by adding 'abs_' prefix
        :param filename: A path to file to read.
            Can also be a python 3 pathlib instance or the URL of an OpenDAP dataset.
        :raises: ValueError if var is None and there is more than one variable in the dataset or, if var
            is not None and is not present in the dataset
        :raises: ValueError if the grid of the component file is incompatible with
            the gird of the existing Dataset
        :raises: ValueError if the absolute values have not yet been read
        """

        # Check if absolute values have been read
        if not self.absolute_values_read:
            raise ValueError("The absolute values have not been read yet.")

        # Read the NetCDF dataset from the file
        new_dataset = Dataset(filename)
        print(new_dataset.variables.keys())
        print(list(new_dataset.variables.keys()))
        
        # If var is None, check that there is only one variable present beside "lat" and "lon"
        if var is None:
            variables = list(new_dataset.variables.keys())
            variables.remove("LAT")
            variables.remove("LON")
            if len(variables) != 1:
                raise ValueError("If var is None, there must be exactly one variable besides 'lat' and 'lon'.")

            # Get the variable name
            var = variables[0]
            print("this is var of the components: ", var)
            
            print(self.components_list)
            self.components_list.append(var)
            print("Dimension:")
            print(new_dataset[var].shape)
        
        
        # Check if the grid of the component file is compatible with the grid of the existing Dataset
        if new_dataset[var].shape != self.dataset[self.main_var].shape:
            raise ValueError("The grid of the component file is incompatible with the grid of the existing Dataset.")

        
        # Create a new variable in the dataset to store the component data
        component_out = self.dataset.createVariable(var, 'f4', new_dataset[var].dimensions)

        # Add the component data to the dataset
        component_out[:] = new_dataset.variables[var][:]
        # Add units to the variable
        component_out.units = "ug/m3"
        print(self.dataset)
        print("done add components")


        return

    def add_components(self, filenames: List[str]):
        """
        Adds multiple components in a single call from multiple files. Assumes that
        every file given contains only one variable beside lat and lon

        Can only be called after the dataset is initialized with absolute values.

        :param filenames:  A list of file paths to read.
            Elements of the list can also be a python 3 pathlib instance or the URL of an OpenDAP dataset.
        :raises: ValueError if there is more than one variable in any of the datasets
        :raises: ValueError if the grid of a component file is incompatible with
            the gird of the existing Dataset
        :raises: ValueError if the absolute values have not yet been read
        """
            # Check if absolute values have been read
        if not self.absolute_values_read:
            raise ValueError("The absolute values have not been read yet.")

        for filename in filenames:
            # Read the NetCDF dataset from the file
            print("filename: ", filename)
            self.add_component(filename)


        print("this is dataset now after add_components:")
        print(self.dataset)
             
        return

    def compute_abs_values(self):
        """
        Computes absolute values for every component present in the dataset by applying a formula.

        :param components: Array of component names
        :return: None
        :raises: ValueError if the absolute values have not yet been read
        """
        # Check if absolute values have been read
        if not self.absolute_values_read:
            raise ValueError("The absolute values have not been read yet.")

        for component in self.components_list:
            # Compute the absolute values for the component
            modified_values = self.dataset.variables[component][:] * self.dataset.variables['PM25'][:] / 100

            # Create a new variable in the output dataset for the modified values
            modified_variable = self.dataset.createVariable(f'{component}_abs', 'f4', ('LAT', 'LON'))
            modified_variable[:] = modified_values[:]
            # Add units to the variable
            modified_variable.units = "ug/m3"
        print("This is the dataset after compute abs values: ")
        print(self.dataset)
        return
    
    def get_dataset(self) -> Dataset:
        return self.dataset

    def write_dataset(self, filename):
        """
        Creates a new file, saving the current state of the dataset

        :param filename: NetCDF DataFrame from the processing part
        :return: None
        """
        # Save the current state of the dataset to a new file
        self.dataset.to_netcdf(filename)

        return

    def __str__(self):
        """
        Constructs string representation of the NetCDF dataset, with variable names and dimensional information
        """
        # Get the variable names in the dataset
        variable_names = list(self.dataset.variables.keys())

        # Construct the string representation
        str_repr = "NetCDF Dataset:\n"
        str_repr += "\n".join(variable_names)

        return str_repr


def main(infile: str, components: List[str], outfile):
    ds = NetCDFDataset()
    #print("testing")
    ds.read_abs_values(infile, outfile)
    print(ds)
    ds.add_components(components)
    print(ds)
    ds.compute_abs_values()
    print(ds)


if __name__ == '__main__':
    #init_logging(level=logging.INFO, name="NetCDF")
    parser = argparse.ArgumentParser (description="Tool to combine components into a single NetCDF file")
    parser.add_argument("--input", "-in", "-i",
                        help="Path to the main NetCDF file containing absolute values",
                        default=None,
                        required=True)
    parser.add_argument("--components", "-c",
                        help="Path to the NetCDF files containing components",
                        nargs='+',
                        default=None,
                        required=True)
    parser.add_argument("--output", "-out", "-o",
                        help="Path to the file with the combined dataset",
                        default=None,
                        required=False)

    args = parser.parse_args()
    main(args.input, args.components, args.output)
