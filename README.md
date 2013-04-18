# growth-yield-batch

### An automated batch process to predict of "growth and yield" for forest vegetation plots

Major goals include:

* Grow IDB plot data according to multiple silvicultural prescriptions using the Forest Vegetation Simulator (FVS).

* Automate the post-processing, parsing and organization of the FVS output; preps the input files for the harvest scheduler.

* Parrallelize the task load onto multiple servers to acheive a target completion time.

* A devops environment using Vagrant/Puppet for development and Amazon EC2 for deployment.






## Running

1. `vagrant up`
2. 











## FVS Directory Structure

In order to batch process runs with this system, it's important that the input files conform to this file structure outlined below... *Work in progress; three potential strategies outlined below*

### Naming requirements

All names should be alphanumeric (no spaces, dashes, underscores, etc)

* **Variants** will be the fvs code used in the .exe file (FVSpn.exe = pacific northwest = `pn` )
* **Rxs** will should have an easily recognizable nomanclature (60 year rotation with commercial thin = `CT60` )
* **Stand ids** will be the numeric Condition ID used as the representative plot (`1332`)
* **Offsets** are handled automatically *if* there is the appropriate line in the keyfile: "Offset = ___"

### Data Directory Structure 
**One key per Rx and Stand**

```
{{Condition ID}}_{{Rx ID}}
   |---- {{Condition ID}}_{{Rx ID}}_original.key
   |---- {{Condition ID}}.fvs
   |---- {{Condition ID}}_{{Rx ID}}.variant     <= this file contains the variant code to be used
```

Example:

```
1332_CT60
   |---- 1332_CT60_original.key
   |---- 1332.fvs
   |---- 1332_CT60.variant 
```

#### Pros

* Small, fast, self contained runs
* Output files (ex: alt_cut_vol.txt, etc) will be 1:1 with stands

#### Cons

* Lots of small processes to manage; QC issues
* Overall speed hit due to overhead time of each run (?)

### Batch runs

Each *data directory* will contain one and only one _original.key file. 

The batch processing system will be set up to accept a *batch directory* which contains multiple *data directories*

Example:

```
BatchRun1
  |-- 6056_CT60
       |---- 6056_CT60_original.key
       |---- 6056.fvs
       |---- 6056_CT60.variant 
  |-- 1332_CT60
       |---- 1332_CT60_original.key
       |---- 1332.fvs
       |---- 1332_CT60.variant 
```
