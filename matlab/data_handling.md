{{../markdown_header.txt}}

# Data Handling in Matlab

[Split apply combine workflow](https://www.mathworks.com/help/matlab/matlab_prog/split-data-into-groups-and-calculate-statistics.html)

## Importing Stata Files

Matlab cannot read Stata files (why not??). The easiest way, at a cost of $80 per year, is Stat/Transfer.

A free alternative would be to use another package to convert that Stata files to CSV. But that seems fragile. Matlab's CSV handling does not always work as expected. One would have to find a way to encode missing values, etc.

### Missing values

Matlab does not have the concept of missing values. 

-----------