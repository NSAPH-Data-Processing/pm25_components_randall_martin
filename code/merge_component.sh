#!/bin/bash

# Set the input and output directories
input_directory="/net/rcstorenfs02/ifs/rc_labs/dominici_lab/lab/data/pm25_components/PM25"
output_directory="../data/output/component_merged"

# Loop over the years from 2000 to 2018
for year in {2000..2018}; do
    # Set the input and output file paths
    input_file="${input_directory}/V4NA03_PM25_NA_${year}01_${year}12-RH35.nc"
    output_file="${output_directory}/year${year}.nc"
    
    # Run the Python command
    python netcdf_tools.py --input "${input_file}" --components \
        "/net/rcstorenfs02/ifs/rc_labs/dominici_lab/lab/data/pm25_components/BCp/GWRwSPEC_BCp_NA_${year}01_${year}12-wrtSPECtotal.nc" \
        "/net/rcstorenfs02/ifs/rc_labs/dominici_lab/lab/data/pm25_components/NH4p/GWRwSPEC_NH4p_NA_${year}01_${year}12-wrtSPECtotal.nc" \
        "/net/rcstorenfs02/ifs/rc_labs/dominici_lab/lab/data/pm25_components/NITp/GWRwSPEC_NITp_NA_${year}01_${year}12-wrtSPECtotal.nc" \
        "/net/rcstorenfs02/ifs/rc_labs/dominici_lab/lab/data/pm25_components/OMp/GWRwSPEC_OMp_NA_${year}01_${year}12-wrtSPECtotal.nc" \
        "/net/rcstorenfs02/ifs/rc_labs/dominici_lab/lab/data/pm25_components/SO4p/GWRwSPEC_SO4p_NA_${year}01_${year}12-wrtSPECtotal.nc" \
        "/net/rcstorenfs02/ifs/rc_labs/dominici_lab/lab/data/pm25_components/SOILp/GWRwSPEC_SOILp_NA_${year}01_${year}12-wrtSPECtotal.nc" \
        "/net/rcstorenfs02/ifs/rc_labs/dominici_lab/lab/data/pm25_components/SSp/GWRwSPEC_SSp_NA_${year}01_${year}12-wrtSPECtotal.nc" \
        --output "${output_file}"
done
