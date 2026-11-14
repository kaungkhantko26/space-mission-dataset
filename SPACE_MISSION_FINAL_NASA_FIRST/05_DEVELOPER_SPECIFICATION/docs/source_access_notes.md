# Official source access notes

## Artemis II Mission Bundle

PDS Geosciences Mission Bundle root:
https://pds-geosciences.wustl.edu/artemis2/urn-nasa-pds-artemis2_mission/

PDS readme:
https://pds-geosciences.wustl.edu/artemis2/urn-nasa-pds-artemis2_mission/readme.txt

The Orion environment collection contains two CSV logger products and matching XML labels. PDS states that the HOBO records cover March 26 through April 21, 2026 and sample temperature, relative humidity and dew point every 60 seconds. Follow the XML labels and User Guide for the exact table fields and units.

## Artemis II SPICE bundle

Archive root:
https://naif.jpl.nasa.gov/pub/naif/pds/pds4/artemis2/artemis2_spice/

Archive description:
https://naif.jpl.nasa.gov/pub/naif/pds/pds4/artemis2/artemis2_spice/document/spiceds_v001.html

Meta-kernel:
https://naif.jpl.nasa.gov/pub/naif/pds/pds4/artemis2/artemis2_spice/spice_kernels/mk/artemis2_v01.tm

The meta-kernel lists supporting kernels in load order. The downloader script optionally retrieves the meta-kernel and each file it references. The complete set includes a DE430 planetary kernel (~114 MB according to the NAIF listing), so the option is explicit rather than run by default. Preserve the original archive directory relationships so the meta-kernel's relative paths resolve.

## Artemis II User Guide

https://pds-geosciences.wustl.edu/artemis2/urn-nasa-pds-artemis2_mission/document/artemis2_data_user_guide.pdf

Read this before using camera/audio/environment products; it explains PDS bundles, collections, product labels, processing, and citation requirements.

## NASA DONKI

API landing page:
https://api.nasa.gov/

Endpoint templates are in `data/donki_optional_endpoint_registry.csv`. The package does not include live event responses. Add a key through NASA's API portal for sustained use. Keep keys out of public browser bundles.

## FIRMS

Area API guide:
https://firms.modaps.eosdis.nasa.gov/api/area
The area service requires a Map Key. This is outside the core Workstream 3 dataset scope.

## SPHEREx

Data access:
https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-access/
Current collections include DR1 and QR3; use them rather than superseded QR2 for new work. SPHEREx products are FITS spectral images/cubes and should be considered only for optional sky-science visualization.
