## Calculation of seasonality.
The program calculates the seasonality within the year for a set of quotes (daily bars)
and displays the price and seasonality chart. Seasonality is calculated based on the
closing prices.

####Stack:
Python / Flask / Pandas / scipy / JavaScript

### 1. Install:
```
pip install -r requirements.txt

```
### 2. Using
Just select *.csv file with quotes and click "Calculate" button.

The file can contain any set of columns, but there must be columns with the headers "Date" and "Close" among them.

For Example:
```
"Symbol";"Date";"Open";"High";"Low";"Close"
GC3-067;04.01.2010;1346,8;1372,4;1341,6;1369,6
GC3-067;05.01.2010;1369,8;1377,4;1363,3;1365,9
GC3-067;06.01.2010;1366,3;1388,8;1364,6;1386,8
GC3-067;07.01.2010;1386,8;1387,3;1376,5;1379,6
```

The sample files to calculate are in the folder "quotes".


   