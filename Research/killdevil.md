{{../markdown_header.txt}}

# Using HPCs at UNC #

## Crashing jobs

When jobs crash without explanation:
* check whether over disc quota. Quota is 52GB in 2020.
* the reason may be errors writing to files. This terminates a process without any info on the reason in the log.
* Matlab ignores file writing errors. It just keeps running. The crash only occurs when file reads fails.

## Uploading Files ##

Set up login via `ssh` keys. Then use `rsync` to upload and download files.

## Changing software versions

`module avail` julia lists available versions.

`module add julia/1.4.1` adds a module temporarily. But need to `module save` to make it permanent.

`module rm` removes a module

`module list` lists currently installed ones.

## Slurm

Each line in the sbatch file looks like `#SBATCH -o value`.

Options (indicated by -o) are:
* -t 03-00: time in days-hours
* -N 1: number of nodes
* --mem 24576: memory in megabytes (per cpu)

Status of running jobs:

* squeue -u <onyen>
* squeue --job XXXX
* `sacct --format="JobID,JobName%30,State,ExitCode"` (best typed using KeyboardMaestro)

## Matlab Issues ##

It is easiest to replicate the local directory structure on `killdevil`. Then running files on the cluster just requires a change in the base directory that all other directories hang off.

Write your code so that the data are placed in the right folder (different on unix cluster vs local machine).

Write a matlab function that does the computations and can be called from the command line.

Command syntax:
bsub -n 8 -R "span[hosts=1]" matlab -nodisplay -nosplash -r "run_batch_so1('fminsearch',1,1,7)" -logfile set7.out
-n 8 : requests 8 cores - the max matlab can handle

`run_batch_so1` is my command file in this example.

Kure jobs crash regularly. It is important to make sure the optimization algorithm can hot-start (resume after a crash using a saved history).

Saving files:

* Matlab cannot save large / complex files. It crashes. Only save the minimum optimization history needed to hot-start.
* When using parallel algorithms, make sure different instances do not try to read / write the same file at the same time. A simple semaphore approach is easily implemented (each instance locks the file it wants to access by writing a file, e.g. "lock07_param.mat" indicates that instance 7 has locked the file param.mat).


------------