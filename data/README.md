# Data provenance

Source: Housing & Development Board, [Resale flat prices based on registration date from Jan-2017 onwards](https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view), published on data.gov.sg under the [Singapore Open Data Licence](https://data.gov.sg/open-data-licence).

The local snapshot contains 239,330 rows covering January 2017 through August 2026. The original download date was not recorded. The source page and licence were checked on 14 September 2026; that verification date is not the snapshot's download date. The live source may contain newer or revised records.

- `raw/hdb_resale_raw.csv`: fixed source snapshot, 11 published columns.
- `processed/hdb_resale_clean.csv`: transaction-level data rebuilt by notebook 02; includes parsed leases, year/quarter, price per sqm, flat age, and storey midpoint.
- Analytical summaries belong in `outputs/`; figures belong in `charts/`.

Raw snapshot SHA-256: `d7a268d7f2285b2bdb6f614b1063095eb08ba65adefbe23ee3c3e07588839d33`

No rows are removed merely because they match other published rows. There is no unique sale identifier, so identical attributes do not establish duplicate transactions. The cleaning notebook preserves all 239,330 rows and rounds price per sqm and numeric lease years to two decimals.

This is an independent analysis and does not imply HDB endorsement. The repository's MIT licence covers the project code; the source dataset remains subject to the Singapore Open Data Licence.
