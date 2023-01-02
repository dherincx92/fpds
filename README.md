# fpds
A no-frills parser for the Federal Procurement Data System (FPDS)
at https://www.fpds.gov/fpdsng_cms/index.php/en/.

## Motivation
The only programmatic access to this data via an ATOM feed limits each
request to 10 records, which forces users to deal with pagination.
Additonally, data is exported as XML, which proves annoying for most
developers. `fpds` will handle all pagination and data
transformation to provide users with a nice JSON representation of the
equivalent XML data.

## Setup

To install this package for development, create a virtual environment and install dependencies.

```
$ python3 -m venv venv
$ source venv/bin/activate
# pip install -e .
```

## Usage

For a list of valid search criteria parameters, consult FPDS documentation
found at: https://www.fpds.gov/wiki/index.php/Atom_Feed_Usage. _Note_: `fpds`
handles parameter quoting so simply enclose your parameter string in one
set of quotes, as seen below.

Via CLI:
```
$  fpds parse params "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504"
```


By default, data will be dumped into an `.fpds` folder at the user's
`$HOME` directory. If you wish to override this behavior, provide the `-o`
option. The directory will be created if it doesn't exist:

```
$  fpds parse params "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504" -o {some-directory}
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

### Testing

```
$ make test
```

## Additional Notes
To ensure no data is lost during export, `fpds` will save tag attributes as
individual data elements. For example, parsing the `contractActionType` tag
and extracting the text value would only return `E` and omit data contained
in the `description` and `part80orPart13` attributes.

```
 <ns1:contractActionType description="BPA" part8OrPart13="PART8">E</ns1:contractActionType>
```

When parsing such elements, `fpds` will represent the tag above in the
following manner:

```
    {
        "contractActionType": "E",
        "contractActionType__description": "BPA"
        "contractActionType__part8OrPart13": "PART8"
    }
```
