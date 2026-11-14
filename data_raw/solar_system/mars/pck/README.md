

\# Mars SPICE PCK Parameters



\## Dataset Overview



This dataset contains selected Mars physical and rotational parameters extracted from the official NASA/JPL NAIF SPICE Planetary Constants (PCK) kernel.



The dataset includes Mars pole orientation coefficients, prime meridian rotation coefficients, and triaxial ellipsoid radii.



\## Source Information



\- \*\*Organization:\*\* NASA/JPL Navigation and Ancillary Information Facility (NAIF)

\- \*\*Kernel Type:\*\* SPICE Planetary Constants Kernel (PCK)

\- \*\*Original File:\*\* `mars\_konopliv\_2026\_v1.tpc`

\- \*\*Kernel Author:\*\* Nat Bachman (NAIF)

\- \*\*Kernel Date:\*\* October 3, 2026

\- \*\*Scientific Reference:\*\* Konopliv et al. (2026)

\- \*\*DOI:\*\* https://doi.org/10.3847/PSJ/ae9ba7

\- \*\*Official Source:\*\* https://naif.jpl.nasa.gov/pub/naif/generic\_kernels/pck/



\## Files



| File | Description |

|---|---|

| `mars\_konopliv\_2026\_v1.tpc` | Original NAIF SPICE PCK kernel |

| `mars\_pck\_parameters.csv` | Selected Mars parameters extracted from the original kernel |



\## Dataset Parameters



| Parameter | Description | Unit |

|---|---|---|

| `BODY499\_POLE\_RA` | Right ascension of Mars' north pole | degree and polynomial coefficients |

| `BODY499\_POLE\_DEC` | Declination of Mars' north pole | degree and polynomial coefficients |

| `BODY499\_PM` | Mars prime meridian rotation angle | degree and polynomial coefficients |

| `BODY499\_RADII` | Triaxial ellipsoid radii (X, Y, Z) | km |



\## Time Reference



\- Pole RA and DEC polynomial terms use Julian centuries past J2000 TDB.

\- Prime meridian polynomial terms use days past J2000 TDB.

\- Polynomial coefficients are preserved as provided in the original kernel.



\## Data Processing



\- Selected parameter values were extracted from the original `.tpc` kernel.

\- The extracted values were organized into CSV format.

\- Original kernel values were preserved without numerical modification.

\- The CSV is a selected parameter extraction, not a complete representation of the PCK kernel.



\## Toolkit Compatibility



The original kernel supports Mars system rotation data with SPICE Toolkit N0067 and newer.



For older Toolkit versions (N0066 and earlier), NAIF provides an alternative kernel:



`mars\_konopliv\_2026\_n0066\_v1.tpc`



\## Provenance



The original kernel header states that its creation was assisted by Claude Sonnet 5.



The kernel also includes rotation and shape information for Phobos and Deimos, although this CSV contains only selected Mars parameters.



\## Usage Notes



This dataset describes planetary orientation and shape parameters. It is not a Mars atmospheric dataset or a spacecraft trajectory dataset.



Refer to the original NAIF kernel and its documentation for complete definitions, equations, and usage instructions.



