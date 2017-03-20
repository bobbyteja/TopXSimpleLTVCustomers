# TopXSimpleLTVCustomers
Calculation of top 'X' LTV customers from events data.

Implementation of Simple LTV calculation

1) Grouped all visits and orders for each customer at week level.
2) Calculated average expenditure amount( orders ) for each customer at week level.
3) Computed 'a' using the below formula by using the computed values from Steps 1 & 2 at week level.
   ( customer expenditures per visit (USD) x number of site visits per week ) 
4) Calculated Simple LTV for each customer at week level for all weeks where visits and orders existed.
5) Summed up all simple LTV's for each customer at different weeks( where visits and orders existed ).
6) Sorted the final LTV's in descending order and extracted the respective names of the customers.


Steps to execute :-

1.) Copy both the files and test data into the same directory.
2.) Execute the script as below with two arguments.

On Mac :-
python code.py 
Enter the no. of files
num >= 1
No of desired customers in the output:
X ( Any positive integer )


On Windows :-
py -v code.py
Enter the no. of files
num >= 1 
No of desired customers in the output:
X ( Any positive integer )



