{{../markdown_header.txt}}

# Using Killdevil at UNC #

It is easiest to replicate the local directory structure on `killdevil`. Then running files on the cluster just requires a change in the base directory that all other directories hang off.

Write your code so that the data are placed in the right folder (different on unix cluster vs local machine).

Write a matlab function that does the computations and can be called from the command line.

Command syntax:
bsub -n 8 -R "span[hosts=1]" matlab -nodisplay -nosplash -r "run_batch_so1('fminsearch',1,1,7)" -logfile set7.out
-n 8 : requests 8 cores - the max matlab can handle

`run_batch_so1` is my command file in this example.

Kure jobs crash regularly. It is important to make sure the optimization algorithm can hot-start (resume after a crash using a saved history).

## Matlab Issues ##

Matlab is stuck in 2013 on all of UNC's unix clusters (as of 2016-Aug). It is therefore basically no longer usable.

Update: We now have `Longleaf` with newer Matlab versions.

Saving files:

* Matlab cannot save large / complex files. It crashes. Only save the minimum optimization history needed to hot-start.
* When using parallel algorithms, make sure different instances do not try to read / write the same file at the same time. A simple semaphore approach is easily implemented (each instance locks the file it wants to access by writing a file, e.g. "lock07_param.mat" indicates that instance 7 has locked the file param.mat).

## Uploading Files ##

It is easiest to mount the `killdevil` home directory as a drive. Then use `rsync` to upload and download files.

Note for `MacOS` users: This does not work with the pre-installed version of `rsync` (as of Nov 2016). You need to install a newer version. The easiest way to do so is `MacPorts`.

------------