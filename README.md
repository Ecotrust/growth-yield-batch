# growth-yield-batch

### An automated batch process to predict growth and yield for forest vegetation plots

Major goals include:

* Grow IDB plot data according to multiple silvicultural prescriptions using the Forest Vegetation Simulator (FVS).

* Automate the post-processing, parsing and organization of the FVS output; preps the input files for the harvest scheduler.

* Parrallelize the task load onto multiple servers to acheive a target completion time.

* A devops environment using Vagrant/Puppet for development and Amazon EC2 for deployment.


## Initial deployment

* Install FVS locally on a Windows machine; [download](http://www.fs.fed.us/fmsc/fvs/software/complete.shtml)
* Copy the contents of `C:/FVSBin` to `./fvsbin` ... they will be gitignored so not checked into the repo
* Start virtual machine with `vagrant up`
* You will have to restart services with `fab dev restart_services`
* To track status of tasks, visit the celery flower interface at http://localhost:8080


## Building the batch directory structure from base data

To build keyfiles in the proper directory structure from base data (.key, .fvs, .stdinfo), 
it's important that the input files conform to this file structure outlined below: 

### Project Directory structure
```
project_directory
|-- config.json
|-- cond
|   |-- 31566.cli
|   |-- 31566.fvs
|   |-- 31566.site
|   `-- 31566.std
`-- rx
    |-- varWC_rx1.key
    `-- varWC_rx25.key

```

##### config.json
JSON formatted file with variables that define the "multipliers"; e.g. variables
for which we're calculate all permutations for each condition.

```
{
  "climate_scenarios": [
    "Ensemble_rcp45",
    "Ensemble_rcp60",
    "Ensemble_rcp85",
    "NoClimate"
  ],
  "sites": {
    "2": "SiteCode          DF       125         1",
    "3": "SiteCode          DF       105         1"
  },
  "offsets": [
    0,
    5,
    10,
    15,
    20
  ]
}
```

##### cond/<condid>.cli

Climate file as per the [FVS climate extension](http://www.fs.fed.us/fmsc/fvs/whatis/climate-fvs.shtml)

##### cond/<condid>.fvs

FVS input tree lists

##### cond/<condid>.std

Single line representing the FVS STDINFO keyword entry. Contains information about
plot location, slope, aspect, etc.

##### rx/*.key files

These use the jinja2 templating language as placeholders for plot-specific variables.
For example, to refer to the condition id in the keyfile:
```
{{condid}}.fvs
```
The build process provides the following variables followed by an example:

```
 'climate': 'Ensemble_rcp45',
 'condid': '31566',
 'keyout': 'varWC_rx1_cond31566_site3_climEnsemble-rcp45_off0.key',
 'offset': 0,
 'out': 'varWC_rx1_cond31566_site3_climEnsemble-rcp45',
 'rx': '1',
 'site_class': '3',
 'sitecode': 'SiteCode          DF       105         1\n',
 'stdident': '31566    varWC_rx1_cond31566_site3_climEnsemble-rcp45',
 'stdinfo': 'STDINFO          617    CFS551        13                            61',
 'variant': 'WC',
```

##### rx/includes

You can also provide variant-level include files for common parts of you keyfile.
For example, if you wanted to have a common output database for all files. You could 
put this in your keyfile:

```
{{include.carbon_xls}}
```

And include a file named `rx/include/carbon_xls.txt` with the following contents:
```
DATABASE
DSNOut
FVSClimateOut.xls
CARBRPTS
END
```

Note the rx/include/**name**.txt corresponds exactly with the {{include.**name**}}
in the keyfile.


### Building Keys

Assuming you have set up your project directory according to the structure above:
```
$ cd project_directory
$ build_keys.py
Generating keyfiles for condition 31566
....
```

This will add a `plots` directory to the project with every combination of 
Rx, condition, site, climate model and offset:
```
|-- plots
|   |-- varWC_rx1_cond31566_site3_climEnsemble-rcp45
|   |   |-- 31566.cli
|   |   |-- 31566.fvs
|   |   |-- 31566.std
|   |   |-- varWC_rx1_cond31566_site3_climEnsemble-rcp45_off0.key
|   |   |-- varWC_rx1_cond31566_site3_climEnsemble-rcp45_off10.key
|   |   |-- varWC_rx1_cond31566_site3_climEnsemble-rcp45_off15.key
|   |   |-- varWC_rx1_cond31566_site3_climEnsemble-rcp45_off20.key
|   |   `-- varWC_rx1_cond31566_site3_climEnsemble-rcp45_off5.key
... etc ...
```

## Running FVS

There are three options for running FVS:

##### 1. Run the FVS exectuable directly. 
For newer versions that accept command line
parameters:
```
/usr/local/bin/FVSwcc --keywordfile=varWC_rx1_cond31566_site3_climEnsemble-rcp45_off0.key
```
Or on windows
```
C:\FVSBin\FVSwc.exe --keywordfile=varWC_rx1_cond31566_site3_climEnsemble-rcp45_off0.key
```
Note that this works in the current working directory and doesn't do any parsing or anything; useful for debugging keyfiles.

##### 2. Running a single plot, all offsets 


```
$ cd project_directory
$ build_keys.py
$ run_fvs.py testdata/plots/varWC_rx1_cond31566_site3_climEnsemble-rcp45/
$ run_fvs.py testdata/plots/varWC_rx1_cond31566_site3_climEnsemble-rcp60/
...
```


##### 3. Run all the project's plots in batch mode 

```
$ cd project_directory
$ build_keys.py
$ batch_fvs.py
```

##### 4. Run all the project's plots in asynchronous batch mode

```
$ cd project_directory
$ build_keys.py
$ batch_fvs_celery.py
```

### Outputs 
All working data is written to `work`. The FVS .out files are parsed and 
written to csvs in the `final` directory. There should be as many .csvs in `final`
as there are directories in `plots`. So to check the status of a long running batch

```
$ ls -1 project_directory/final/var*csv | wc -l
```

## Combining csvs

```
cd /usr/local/data/out
# copy header
sed -n 1p `ls var*csv | head -n 1` > merged.csv
#copy all but the first line from all other files
for i in var*.csv; do sed 1d $i >> merged.csv ; done
```

For next steps on importing data to the Forest Planner
please review https://github.com/Ecotrust/land_owner_tools/wiki/Fixture-management#fvsaggregate-and-conditionvariantlookup

## Notes

* To check celery worker status (or execute other celery-related commands) on the remote machine `cd /var/celery && celery status`


### FVS Directory Structure and Naming requirements

Each run is named according to the following scheme:
```
var[VARIANT]_rx[RX]_cond[CONDID]_site[SITECLASS]_clim[CLIMATE SCENARIO]_off[OFFSET YEARS]
```

For example, using the Pacific Northwest variant, prescription 25, condition 43, and site class 2 with the Ensemble/rcp45 climate scenario and a 5 year offset:
```
varPN_rx25_cond43_site2_climEnsemble-rcp45_off5
```