# fpds
A parser for the Federal Procurement Data System (FPDS) at https://www.fpds.gov/fpdsng_cms/index.php/en/

## Setup

To install this package for development, create a virtual environment and install dependencies.

```
$ python3 -m venv venv
$ source venv/bin/activate
# pip install -e .
```

## Usage

Via CLI:
```
$  fpds parse params "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504"
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

You can build and serve up docs, including dbt's super neat lineage graph.
```
$ make serve
```

Lastly, you can clean the clutter and unwanted noise.

```
$ make clean
```

### Testing

```
$ make test
```
