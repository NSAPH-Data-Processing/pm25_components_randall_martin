library(ncdf4)
library(raster)
library(tidyverse)
library(geometry)
library(data.table)
library(maps)
library(magrittr)
library(ggplot2)
library(sf)
library(reshape2) # For reshaping data
library(mapdata)  # For map data
library(ggmap)

nc_file <- nc_open("../data/input/pm25_components/PM25/V4NA03_PM25_NA_200001_200012-RH35.nc")

pm25 <- ncvar_get(nc_file, "PM25")
lon <- ncvar_get(nc_file, "LON")
lat <- ncvar_get(nc_file, "LAT")

# Reshape data
pm25_df <- melt(pm25)
pm25_df$lon <- rep(lon, each = length(lat))
pm25_df$lat <- rep(lat, length(lon))
pm25_df <- na.omit(pm25_df) # Remove NA values
# Remove the "Var1" and "Var2" columns from pm25_df
pm25_df <- pm25_df %>% select(-c(Var1, Var2))

# Save pm25_df as Rdata to the specified path
saveRDS(pm25_df, file = "../data/output/pm25_df.Rdata")