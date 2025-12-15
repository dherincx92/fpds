<div align="center">


                                  __________  ____  _____
                                 / ____/ __ \/ __ \/ ___/
                                / /_  / /_/ / / / /\__ \
                               / __/ / ____/ /_/ /___/ /
                              /_/   /_/   /_____//____/

                        Welcome to a more user-friendly FPDS 🚀
A light-weight, pythonic parser for the Federal Procurement Data System (FPDS) ATOM Feed.
Reference [here](https://www.fpds.gov/fpdsng_cms/index.php/en/).
</div>


## Motivation
To make FPDS data more accesible to developers.

This library helps users by doing the following:
- Automatically handling pagination
- Converting XML and all associated attributes into JSON format


## Setup
As of version 1.5.0, this library manages dependencies using `uv`. It is
_highly_ recommended since this library is tested with it. Note that this
README assumes you will install `uv` and therefore runs all commands within
its context.

### Installing `uv`

You can follow any of the methods found [here](https://docs.astral.sh/uv/getting-started/installation/).
If on Linux or MacOS, we recommend using Homebrew:

```
$ brew install uv
```

Once `uv` is installed, you can use the project Makefile to ensure your local environment
is synced with the latest library installation. Start by running `make install` — this
will check the status of the `uv.lock` file, and install all project dependencies + extras.

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

Run unit tests on your local environment:

```
$ make local-test
```

## Usage
For a list of valid search criteria parameters, consult FPDS documentation
found [here](https://www.fpds.gov/wiki/index.php/Atom_Feed_Usage).

### CLI
Parameters will follow the `URL String` format shown in the link above, with the
following exceptions:

 + Colons (:) will be replaced by equal signs (=)
 + Certain parameters enclose their value in quotations. `fpds` will
automatically determine if quotes are needed, so simply enclose your
entire criteria string in quotes.

 For example, `AGENCY_CODE:"3600"` should be used as `"AGENCY_CODE=3600"`.

```
$  uv run fpds parse "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504"
```

By default, data will be dumped into an `.fpds` folder at the user's
`$HOME` directory. If you wish to override this behavior, provide the `-o`
option. The directory will be created if it doesn't exist.

```
$  uv run fpds parse "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504" -o ~/.my-preferred-dir
```

As of v1.5.0, you can opt out of regex validation by setting the `-k` flag
to `False` — this is helpful in scenarios when either the regex pattern has
been altered by the ATOM feed or a new parameter name is supported, but not
yet added to the configuration in this library.

_NOTE_: if you use `-k`, you will disable regex validation for all parameters,
which means you will be responsible for handling quoting yourself. This is
intentional.

```
$  uv run fpds parse -k "A_NEW_PARAM=a-new-value"
```

Let's say you ran the above command, but were unsure about the quoting strategy
and you wanted to run this using the CLI. As of v1.6.0, the `fields` command
provides a quick reference of available filtering fields. To print them out, run
the following command. Use the `--export` flag to export the full metadata for
fields (this is helpful if you wish to see quoting configuration and the regex validation pattern).

```
$ uv run fpds fields --export true
```

### Python

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

Between v1.2.1 and v1.3.0, significant improvements were made with `asyncio`. Here are
some rough benchmarks in estimated data extraction + post-processing times:

| v1.2.1 | v.1.3.0 |
-------- | --------
188.46   | 29.40
190.38   | 28.14
187.20   | 27.66

Using `v.1.2.1`, the average completion time is 188.68 seconds (~3min).
Using `v.1.3.0`, the average completion time is 28.40 seconds.

This equates to a <u>**84.89%**</u> decrease in completion time!

# Notes

Please be aware that this project is an after-hours passion of mine. I do my best
to accomodate requests, but I receive no $$$ for any of the work I do here.
