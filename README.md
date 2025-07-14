# fpds
A light-weight, pythonic parser for the Federal Procurement Data System (FPDS) ATOM Feed.
Reference [here](https://www.fpds.gov/fpdsng_cms/index.php/en/).


## Motivation
The FPDS ATOM feed limits each request to 10 records, which forces users to deal with pagination. Additonally, data is exported as XML, which proves annoying. `fpds` will handle all pagination and data
transformation to provide users with a nice JSON representation of the
equivalent XML data and attributes.


## Setup
As of version 1.5.0, this library manages dependencies using `uv`. It is
_highly_ recommended since this library is tested with it.


### Installing `uv`

You can follow any of the methods found [here](https://docs.astral.sh/uv/getting-started/installation/). If on Linux or MacOS, we recommend using Homebrew:

```
$ brew install uv
```

Once `uv` is installed, you can use the project Makefile to ensure your local environment is synced with the latest library installation. Start by running `make install` — this will check the status of the `uv.lock` file, and install all project dependencies + extras

### Local Development

For linting and formatting, we use `ruff`. See `pyproject.toml`
for specific configuration.

```
$ make formatters
```

You can clean the clutter and unwanted noise from tools using:

```
$ make clean
```

### Testing
```
$ make local-test
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
option. The directory will be created if it doesn't exist.

As of v1.5.0, you can opt out of regex validation by setting the `-k` flag
to `False` — this is helpful in scenarios when either the regex pattern has
been altered by the ATOM feed or a new parameter name is supported, but not
yet added to the configuration in this library.

```
$  fpds parse "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504" -o ~/.my-preferred-dir
```

Same request via python interpreter:
```
import asyncio
from fpds import fpdsRequest

request = fpdsRequest(
    LAST_MOD_DATE="[2022/01/01, 2022/05/01]",
    AGENCY_CODE="7504"
)

# returns records as an async generator
gen = request.iter_data()

# evaluating generator entries
records = []
async for entry in gen:
    records.append(entry)

# or letting `data` method evaluate generator for you
records = asyncio.run(request.data())
```


# Highlights

Between v1.2.1 and v1.3.0, significant improvements were made with `asyncio`. Here are some rough benchmarks in estimated data extraction + post-processing
times:

| v1.2.1 | v.1.3.0 |
-------- | --------
188.46   | 29.40
190.38   | 28.14
187.20   | 27.66

Using `v.1.2.1`, the average completion time is 188.68 seconds (~3min).
Using `v.1.3.0`, the average completion time is 28.40 seconds.

This equates to a <u>**84.89%**</u> decrease in completion time!

# Notes

Please be aware that this project is an after-hours passion of mine. I do my best to accomodate requests the best I can, but I receive no $$$ for any of the work I do here.
