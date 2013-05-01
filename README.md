# growth-yield-batch

### An automated batch process to predict of "growth and yield" for forest vegetation plots

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
* Run the automated batch test with `fab dev run_test_batch`
* To track status of tasks, visit the celery flower interface at http://localhost:5555

## Outline

### Building the batch directory structure from base data

To build keyfiles in the proper directory structure from base data (.key, .fvs, .stdinfo), 
you need to start with data like this:

```
testdata/
|-- fvs
|   |-- 42.fvs
|   |-- 42.stdinfo   <---- this file simply contains a single line with the STDINFO keyword
|   |-- 43.fvs
|   `-- 43.stdinfo
`-- rx
    |-- varPN_rx25_CONDID_site2.key
    `-- varPN_rx25_CONDID_site3.key
```

and then run 
```
vagrant@precise32:/usr/local/apps/growth-yield-batch$ buildkeys basedata/ batch1
Working on condition 42
  constructing varPN_rx25_cond42_site2
  ....
```

which constructs the batch directory structure like
```
testdata/
`-- fvs
`-- rx
`-- keys
    `-- varWC_rx9_cond91_site2
        |-- 91.fvs
        |-- varWC_rx9_cond91_site2_growonly.key
        `-- varWC_rx9_cond91_site2_original.key
```

### Running a single test plot directly

Run a single test site directly

```
$ fvs testdata/keys/varPN_rx25_cond42_site2/
Using data dir testdata/varPN_rx25_cond42_site2 ...
....
Results in directory /usr/local/data/out/varPN_rx25_cond42_site2/
```


### Run all the testdata plots in asynch/batch mode

Adds them all to the celery queue

```
vagrant@precise32:/usr/local/apps/growth-yield-batch$ fvsbatch testdata/keys/
Sent task to queue      fvs('/usr/local/apps/growth-yield-batch/testdata/keys/varPN_rx25_cond42_site2')    5eca96d0-ba17-45ca-a5f2-b3c527e37611    PENDING
Sent task to queue      fvs('/usr/local/apps/growth-yield-batch/testdata/keys/varPN_rx25_cond43_site2')    3f388542-d52a-4e60-83d8-fb27dfb68bfe    PENDING
....
```


### Check status at command line

```
vagrant@precise32:/usr/local/apps/growth-yield-batch$ fvsstatus
{
  "PENDING": 2,
  "SUCCESS": 1
}
5eca96d0-ba17-45ca-a5f2-b3c527e37611    SUCCESS /usr/local/apps/growth-yield-batch/testdata     varPN_rx25_cond42_site2       /usr/local/data/out/varPN_rx25_cond42_site2
3f388542-d52a-4e60-83d8-fb27dfb68bfe    PENDING /usr/local/apps/growth-yield-batch/testdata     varPN_rx25_cond43_site2       None
```








## Notes

* To check celery worker status (or execute other celery-related commands) on the remote machine `cd /var/celery && celery status`


### FVS Directory Structure and Naming requirements

In order to batch process runs with this system, it's important that the input files conform to this file structure outlined below... *Work in progress; three potential strategies outlined below*

Each run is named according to the following scheme:
```
var[VARIANT]_rx[RX]_cond[CONDID]_site[SITECLASS]
```
For example, using the Pacific Northwest variant, prescription 25, condition 43, and site class 2:
```
varPN_rx25_cond43_site2
```

* **Variants** will be the fvs code used in the .exe file (FVSpn.exe = pacific northwest = `pn` )
* **Rxs** will should have an easily recognizable nomanclature (60 year rotation with commercial thin = `CT60` )
* **Condition ids** will be the numeric Condition ID used as the representative plot (`1332`)
* **Site class** is a categorized site index
* **Offsets** are handled automatically *if* there is the appropriate line in the keyfile: "Offset = ___"

