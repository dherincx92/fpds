# fpds
A no-frills parser for the Federal Procurement Data System (FPDS) found
[here](https://www.fpds.gov/fpdsng_cms/index.php/en/).


## Motivation
The only programmatic access to this data via an ATOM feed limits each
request to 10 records, which forces users to deal with pagination.
Additonally, data is exported as XML, which proves annoying for most
developers. `fpds` will handle all pagination and data
transformation to provide users with a nice JSON representation of the
equivalent XML data.


## Setup
To install this package for development, create a virtual environment
and install dependencies.

```
$ python3.10 -m venv venv
$ source venv/bin/activate
$ pip install -e .
```

## Usage
For a list of valid search criteria parameters, consult FPDS documentation
found [here](https://www.fpds.gov/wiki/index.php/Atom_Feed_Usage). Parameters
will follow the `URL String` format shown in the link above, with the
following exceptions:

 + Colons (:) will be replaced by equal signs (=)
 + Certain parameters enclose their value in quotations. `fpds` will
automatically determine if quotes are needed, so simply enclose your
entire criteria string in quotes.

 For example, `AGENCY_CODE:"3600"` should be used as `"AGENCY_CODE=3600"`.

Via CLI:
```
$  fpds parse "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504"
```

By default, data will be dumped into an `.fpds` folder at the user's
`$HOME` directory. If you wish to override this behavior, provide the `-o`
option. The directory will be created if it doesn't exist:

```
$  fpds parse "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504" -o my-preferred-directory
```

Same request via python interpreter:
```
import asyncio
from fpds import fpdsRequest

request = fpdsRequest(
    LAST_MOD_DATE="[2022/01/01, 2022/05/01]",
    AGENCY_CODE="7504"
)
data = list(asyncio.run(request.data()))
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

### Testing
```
$ make local-test
```

## What's New
As of 08/21/2024, `v1.4.1` data is returned as a generator, providing more flexibility
for memory constrained devices. Users also have the ability to select specific
pages of results with the `page` parameter.

Parameters in `fields.json` have been updated to support unbounded values. Previously, range-based parameters had to define an upper & lower bound (i.e. `[4250, 7500]`). In the most current version of this library, you can now specify the following patterns for all range parameters: `[4250,)` or `(, 7500]`. This even works for dates: `[2022/08/22,)` or `(, 2022/08/01]`!

`fpds` now supports asynchronous requests! As of `v1.3.0`, users can instantiate
the class as usual, but will now need to call the `process_records` method
to get records as JSON. Note: due to some recursive function calls in the XML
parsing, users might experience some high completion times for this function
call. Recommendation is to limit the number of results.

#### Timing Benchmarks (in seconds):

| v1.2.1 | v.1.3.0 |
-------- | --------
188.46   | 29.40
190.38   | 28.14
187.20   | 27.66

Using `v.1.2.1`, the average completion time is 188.68 seconds (~3min).
Using `v.1.3.0`, the average completion time is 28.40 seconds.

This equates to a <u>**84.89%**</u> decrease in completion time!


As of `v1.3.0`, `fpds` now supports the use of over 100 keyword tags when searching
for contracts using the `v1.5.3` ATOM feed.
