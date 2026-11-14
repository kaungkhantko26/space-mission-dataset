# Final data policy / eligibility

1. Authorized science publishers: NASA and NASA-managed repositories (JPL/NAIF, PDS, NASA NTRS, NASA Open Data, Artemis, DONKI, FIRMS, SPHEREx). Kaggle is approved *only as a secondary candidate*, never authoritative.
2. No China-, Russia-, or other non-US-affiliated institutional scientific source data in the approved source folder. Company, mission and hardware affiliations are not reliably determinable from arbitrary crowdsourced labels, so ambiguous Kaggle records are removed from the authoritative package.
3. No external manufacturer-only SpaceX/ULA/Northrop engineering data in the production dataset, despite US business registration; old research files are excluded and documented in the audit. NASA-sourced SLS launch records remain.
4. Two mission-scoped foundations only: Sun-Earth-Moon and Sun-Earth-Mars. Common Sun/Earth/time/NAIF kernels are not duplicated.
5. Distinguish official raw data, processed/parsed, reference approximate, project-created examples, optional context, QA hold, and secondary candidates.
6. Raw source documents and prior versions remain in the user's original uploaded archive, **not duplicated in this cleaned release**. The original upload is preserved in the current session and should be saved separately by the user. This prevents shipping excluded/unverified data.
7. `QA_HOLD` must never be used as approved production data until the timestamp defects are resolved against the original NAIF SPK.
8. The exact verified source accession, NASA-managed provenance and any mixed institutional contributors should be rechecked by project owners before external publication. These are local archive audits, not an independent NASA re-download.
