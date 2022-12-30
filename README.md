# FPDS
A parser for the Federal Procurement Data System (FPDS) at
https://www.fpds.gov/fpdsng_cms/index.php/en/.

This package has been designed to automatically handle any HTTP request to
the FPDS ATOM feed. Users can provide any number of data filters and this
module will represent any FPDS XML data structure as JSON.

## Setup

To install this package for development, create a virtual environment
and install dependencies.

```
$ python3 -m venv venv
$ source venv/bin/activate
# pip install -e .
```

## Usage

The `parse` command allows users to filter federal contracts with an unlimited
number of data filters. _Individual_ parameters must be enclosed in quotes.
By default, this package will dump data into an `.fpds` folder created at
$HOME. If you wish to override this location, simply provide the desired
directory with the `-o` option:

```
$  fpds parse "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504"
```

Same request via python interpreter:

```
from fpds import fpdsRequest

request = fpdsRequest(
    LAST_MOD_DATE="[2022/01/01, 2022/05/01]",
    AGENCY_CODE="7504"
)

# Records saved as a python list
records = request()
```

For linting and formatting, we use `flake8` and `black`.

```
$ make lint
$ make formatters
```

Lastly, you can clean the clutter and unwanted noise.

```
$ make clean
```

## Testing
```
$ make test
```