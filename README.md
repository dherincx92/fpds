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
To install this package for development, create a virtual environment
and install dependencies.

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -e .
```


## Usage
For a list of valid search criteria parameters, consult FPDS documentation
found at: https://www.fpds.gov/wiki/index.php/Atom_Feed_Usage. Parameters
will follow the `URL String` format shown in the link above, with the
following exceptions:

 + Colons (:) will be replaced by equal signs (=)
 + Certain parameters enclose their value in quotations. `fpds` will
automatically determine if quotes are needed, so simply enclose your
entire criteria string in quotes.

 For example, `AGENCY_CODE:”3600”` should be used as `"AGENCY_CODE=3600"`.


Via CLI:
```
$  fpds parse "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504"
```


By default, data will be dumped into an `.fpds` folder at the user's
`$HOME` directory. If you wish to override this behavior, provide the `-o`
option. The directory will be created if it doesn't exist:

```
$  fpds parse "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504" -o {some-directory}
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

# or equivalently, explicity call the `parse_content` method
records = request.parse_content()
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

## What's New
As of v1.2.0, tag names include their full XML tag hierarchy due to duplicate
tag names being overwritten in v1.1.X. For example, the `content` XML below has the
following duplicate tag names: `agencyID`, `PIID`, and `modNumber`.
Based on the original hierarchy, it's clear that one set of tags represents
the actual award info and the second, the award's referenced IDV.

```
<content xmlns:ns1="https://www.fpds.gov/FPDS" type="application/xml">
    <ns1:awardID>
        <ns1:awardContractID>
            <ns1:agencyID name="ENVIRONMENTAL PROTECTION AGENCY">6800</ns1:agencyID>
            <ns1:PIID>0002</ns1:PIID>
            <ns1:modNumber>P00018</ns1:modNumber>
            <ns1:transactionNumber>0</ns1:transactionNumber>
        </ns1:awardContractID>
        <ns1:referencedIDVID>
            <ns1:agencyID name="ENVIRONMENTAL PROTECTION AGENCY">6800</ns1:agencyID>
            <ns1:PIID>EPS31703</ns1:PIID>
            <ns1:modNumber>0</ns1:modNumber>
        </ns1:referencedIDVID>
    </ns1:awardID>
</content>
```

In lieu of this, the final JSON structure would represent this snippet of data
the following (note that additional attributes like `name` in `agencyID` are
still captured and represented by their proper hierarchy; the name of the
attribute is appended to the end of the tag name):

```
{
    "awardID__awardContractID__agenycID": "6800"
    "awardID__awardContractID__agenycID__name": "ENVIRONMENTAL PROTECTION AGENCY"
    "awardID__awardContractID__PIID": "0002"
    "awardID__awardContractID__modNumber": "P00018"
    "awardID__awardContractID__transactionNUmber: "0"
    "referencedIDVID__awardContractID__agenycID": "6800"
    "referencedIDVID__awardContractID__agenycID__name": "ENVIRONMENTAL PROTECTION AGENCY"
    "referencedIDVID__awardContractID__PIID": "EPS31703"
    "referencedIDVID__awardContractID__modNumber": "0"
}
```