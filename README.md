# netcdf_aggregator
Process and aggregate netcdf exposures data from [Randall Martin's data](https://sites.wustl.edu/acag/datasets/surface-pm2-5/). We use [downscale](https://en.wikipedia.org/wiki/Downscaling) rasterization strategy and [TIGER/ Lines Shapefiles](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2000.html#list-tab-790442341). 



The pipeline to do the rasterization and aggregation can be found here:
 https://github.com/NSAPH-Data-Platform/nsaph-gis/blob/develop/nsaph_gis/


Example result: 
| PM25 | zcta | Year |
| :---         |     :---:      |          ---: |
| 6.678696   | 43451     | 2018    |
| 7.124078     | 43452       | 2018      |

### The notebook file contains the basic exploration for Netcdf data and EDA for rasterization result. 

Here is the example of coverage map for year 2018: 

![Example coverage PM2.5](screenshot.png)

## <a name="_3pvqmuyiayzd"></a>Steps to reproduce running Gridmet pipeline in CANNON for  PM25 components aggregation:
Summarized from: <https://3.basecamp.com/3348350/buckets/29048408/messages/6023800231#__recording_6067667051> 
### <a name="_tv0cojf0x4ko"></a>Data Location: 
- Location of smoke pm25 components data: <https://vdi.rc.fas.harvard.edu/pun/sys/dashboard/files/fs//net/rcstorenfs02/ifs/rc_labs/dominici_lab/lab/data/pm25_components>  
- Location of shapefiles data: <https://vdi.rc.fas.harvard.edu/pun/sys/dashboard/files/fs//net/rcstorenfs02/ifs/rc_labs/dominici_lab/lab/data/zipcode/polygon>  
- Location of pipelines: <https://vdi.rc.fas.harvard.edu/pun/sys/dashboard/files/fs//net/rcstorenfs02/ifs/rc_labs/dominici_lab/lab/data_processing> 

### <a name="_fzpsk6d543ow"></a>Connecting to CANNON VPN: 
- Follow these steps: <https://nsaph.info/cannon.html>  
- Open fasrc vpn: for username, type `username@fasrc`
- Setup remote desktop on CANNON, usually I use partition `serial\_requeue` because it is the fastest one 

### <a name="_u0xqpvutvpc3"></a>Clone Github Repos: 
Make sure you have cloned and run `pip install .` from all of these repos:

- [nsaph-core-platform](https://github.com/NSAPH-Data-Platform/nsaph-core-platform/tree/develop)
- [nsaph-gis](https://github.com/NSAPH-Data-Platform/nsaph-gis)
- [nsaph-gridmet](https://github.com/NSAPH-Data-Platform/nsaph-gridmet)
- [nsaph-platform-deployment](https://github.com/NSAPH-Data-Platform/nsaph-platform-deployment)
- [Nsaph-utils](https://github.com/NSAPH-Data-Platform/nsaph-utils)
### <a name="_koxy2eqfcoee"></a>Setting up the environment: 
Run these commands: 
```
module load Anaconda

source activate /net/rcstorenfs02/ifs/rc\_labs/dominici\_lab/lab/environments/exposures\_no\_r

PS1='\u@\h:\W$
```

### <a name="_uxh7esti8run"></a>Run PM25 Aggregation from NetCDF LON and LAT level to crosswalk with ZCTA: 


Run this command: 
```
python -u -m pollution.wustl\_file\_processor --geography zcta --raw\_downloads /net/rcstorenfs02/ifs/rc\_labs/dominici\_lab/lab/data/pm25\_components/PM25/V4NA03\_PM25\_NA\_200001\_200012-RH35.nc --shape\_file\_collection tiger --destination /net/rcstorenfs02/ifs/rc\_labs/dominici\_lab/lab/data\_processing/netcdf\_aggregator/kezia/data/intermediate --var pm25 --strategy downscale 
```

Parameters: 

- –geography: geospatial instance (e.g: zip, zcta, county)
- –raw\_downloads: input file
- –shape\_files: location of shapefile 
- –shape\_file\_collection: collection of shapefile (e.g: tiger)
- –destination: output folder
- –var: variable name (e.g: pm25)
- –strategy: rasterization strategy (e.g: downscale)
### <a name="_crov0h4p3m7q"></a>To run with parallelization: 
Steps to update the environment on Cannon (already done, no need to repeat):
```
cd /net/rcstorenfs02/ifs/rc\_labs/dominici\_lab/lab/data\_processing/nsaph-gridmet

git pull

conda env update -p /net/rcstorenfs02/ifs/rc\_labs/dominici\_lab/lab/environments/exposures\_no\_r -f data\_processing/nsaph-gridmet/env/exposures\_no\_r.yaml
```
Then, cd to the directory where you would like to run the pipeline. I used:

```
cd /net/rcstorenfs02/ifs/rc\_labs/dominici\_lab/lab/data\_processing/netcdf\_aggregator
```


The command I used to run the pipeline is:

```
nohup cwltool --leave-tmpdir --parallel /net/rcstorenfs02/ifs/rc\_labs/dominici\_lab/lab/data\_processing/nsaph-gridmet/src/cwl/pm25\_yearly\_download.cwl --downloads /net/rcstorenfs02/ifs/rc\_labs/dominici\_lab/lab/data/pm25\_components/PM25/ --geography zcta --shape\_file\_collection tiger 2>&1 > 1aggr.log &
```

Please note, that after successful completion of the pipeline, the directory will contain a [bunch of files](https://github.com/NSAPH-Data-Platform/nsaph-gridmet/blob/develop/src/cwl/pm25_yearly_download.cwl#L90-L110):

- Aggregation results (\*.csv.gz)
- Shape files
- logs (\*.log, \*.err) 

` `You would need to copy or move \*.csv.gz to the location of your preference.

The main log file is 1aggr.log, hence you can monitor the progress with the following command:

```
tail -f 1aggr.log
```

### <a name="_bsp9qgmk7ml3"></a>NetCDF Aggregation Before and After: 
Input data: 

File ../data/input/pm25\_components/PM25/V4NA03\_PM25\_NA\_200001\_200012-RH35.nc (NC\_FORMAT\_NETCDF4\_CLASSIC):

1 variables (excluding dimension variables):

float PM25[LON,LAT] (Chunking: [1329,650]) (Compression: level 5)

standard\_name: PM25

units: ug/m3

2 dimensions:

LON Size:9300

standard\_name: longitude

long\_name: longitude centre

units: degrees\_east

LAT Size:4550

standard\_name: latitude

long\_name: latitude centre

units: degrees\_north


Result: 

|PM25|zip|Year|
| :- | :- | :- |
|6\.54720558|12117|2000|
|8\.39553506|12118|2000|
|6\.88292713|12120|2000|
|8\.26666619|12121|2000|
|6\.43065046|12122|2000|
|8\.23465298|12123|2000|
|7\.38409146|12125|2000|
|9\.45000076|12130|2000|
|7\.11666679|12131|2000|
|6\.07616201|12134|2000|
|7\.96428571|12136|2000|
|6\.75964891|12137|2000|


