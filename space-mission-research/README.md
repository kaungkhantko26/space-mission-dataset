# STAGING — do not use as a dataset

This folder is the **maintainers' staging build**. It still contains recalled (`unverified`), `estimated` and `fictional` values (optimizer catalog, costs, instruments, components, the user-supplied SpaceX table, ...). It is **not served, exported or documented as data**.

The public dataset is [`../verified/`](../verified/) (strict mode: verified values only), generated from this staging build plus the retrieved sources by `tools/make_verified.py`. Verification inputs and results live in `metadata/verification_*.json` and `../data_raw/retrieved/`.
