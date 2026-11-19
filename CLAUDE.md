# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Verification of SWPC geomagnetic (Kp / ap / Ap) forecasts. The pipeline downloads SWPC forecast reports and GFZ observed Kp/ap/Ap. It extracts both into tidy CSVs, builds baseline forecasts (real, persistence, recurrence) to compare against, and plots report-availability calendars. Analysis lives in `notebooks/`.

## Environment and commands

All commands run from the repo root. Paths in `src/` are relative to the root, and scripts are invoked as modules.

- Environment: `conda env create -f environment.yml` → `conda activate kpproj`. The default `python` on this machine is a pyenv 3.8 with no pandas, so activate `kpproj` (or call `~/miniforge3/envs/kpproj/bin/python`) first.
- Full pipeline: `snakemake --cores 1`. The first rule runs `scripts/download_swpc_forecasts_and_raw_vals.sh` with wget, which pulls large amounts of data from NOAA NCEI, GFZ and Google Drive.
- Single pipeline step: `python -m scripts.extract_forecasts`, `python -m scripts.get_raw_kp_ap`, `python -m scripts.create_baseline_forecasts`, or `python -m scripts.make_calanders [--config configs/calanders.yml]`.
- Lint (the only CI check, `.github/workflows/ci.yml`): `pycodestyle $(git ls-files "*.py")`.
- Tests (unittest, not run in CI): `python -m unittest discover -s testing -t .`
  - Single file: `python -m unittest testing.test_extract_forecasts_utils`
  - Single test: `python -m unittest testing.test_extract_forecasts_utils.TestFillNansFunc.test_nans_filled`

## Architecture

**Layout:** each pipeline stage has a thin script in `scripts/` that calls functions from a matching `src/<name>_utils.py`. The scripts have no `main()` and run their work at import time. Each utils module has a test file `testing/test_<name>_utils.py`. `Snakefile` wires the stages together and lists both the script and its utils file as inputs, so editing either one re-triggers the rule.

**Data flow:**
1. `raw_data/` (gitignored, filled by the download checkpoint). `geomag_forecast/YYYYMMDDgeomag_forecast.txt` reports, `SWPC_Kp_Forecasts_2011_2025.csv` (internal SWPC 7-day Kp sheet), and GFZ `Kp_ap_*_since_1932.txt`. `download_data_from_internet` is a Snakemake **checkpoint**, so downstream rules find the geomag files dynamically with `geomag_forecast_files()`.
2. `extracted_data/`:
   - `src/extract_forecasts_utils.py` parses the forecast reports into wide CSVs.
   - `src/get_raw_kp_ap_utils.py` parses the GFZ fixed-width text (via `skiprows`) into long `Datetime,<value>` CSVs.
   - `convert_Kp_forecast_to_ap` maps Kp to ap through the standard thirds table. Values must round to an exact table entry, or `.index()` raises.
3. `baseline_forecasts/`: `src/create_baseline_forecasts_utils.py` reads the observed CSVs in `extracted_data/` and writes the shared forecast CSV schema (below). A vectorized core (`make_baseline_values` + `create_baseline_forecast`) sits behind the 9 `create_3day_*` wrappers.
   - Each forecast is issued at T, the moment an observed slot finishes. `Forecast Issued = Forecast Start = T` and `Start Offset (hr) = 0`, so `3hrKp` is the slot [T, T+3h) and `1dAp` is the UT day starting at T.
   - 3-hourly baselines have all 8 issue times per day. Daily Ap has one per day, issued at 00 UT.
   - `real_*`: the observed values of the next 24 slots / 3 days.
   - `persistence_*`: the last completed slot (or day) before T, repeated.
   - `recurrence_*`: each target slot's value from 27 days (one solar rotation) earlier.
   - Values are computed from the full 1932+ series, but only rows with `Forecast Issued >= start_date` (default `2011-01-01`) are kept, so the committed CSVs stay small.
4. `analysis/*_calander.png`: `src/make_calanders_utils.py`, driven by `configs/calanders.yml`. Each report type has an `include` flag and date range; `geomag_forecast` and `SWPC_7day_3hr_ap` are enabled. Reports in `CSV_REPORTS` (the SWPC sheet) get availability from all-NaN rows of the `extracted_data/` CSV via `get_csv_dates`, not from raw report files.

The generated `extracted_data/`, `baseline_forecasts/` and `analysis/` outputs are committed to git.

**Forecast CSV schema** (shared by extracted and baseline forecasts):
- Every row starts with `Forecast Issued, Forecast Start, Start Offset (hr)` (`TIME_COLS` in `extract_forecasts_utils`).
  - `Forecast Issued` is the true issue time parsed from the report's `:Issued:` header (e.g. 22:05, off the 3 hr grid). The SWPC sheet has no time. It is declared issued at 21:00 UTC on `Forecast Day`, just before the ~22 UT geomag_forecast it is anchored to (reasoning in `HUMAN.md`), so `Start Offset (hr)` = 3.
  - `Forecast Start` is 00 UT on the first day of the report's own table, so `3hrKp` is the slot starting there. It's the on-grid key for joining forecasts. geomag/daypre start the day after issue; for the SWPC sheet it is `Forecast Day` + 1 (its values match the geomag report issued on `Forecast Day`).
  - `Start Offset (hr)` = Start − Issued. It can be negative (three_day_forecast tables begin before issue).
- `fill_nans_func(df, freq)` places each report in the slot that holds its issue time (`Forecast Issued` floored to `freq`). Missing slots get NaT `Forecast Issued`, NaN values, and an inferred `Forecast Start`.
- 3-hourly lead columns are `3hrKp … 72hrKp` (or `…ap`), and run to `168hr` for the SWPC 7-day sheet.
- Daily columns are `1dAp, 2dAp, 3dAp`.
- File names follow `<source>_<horizon>_<cadence>_<quantity>.csv`.

**Report types:**
- `geomag_forecast`, `three_day_forecast` and the SWPC sheet are active.
- `daypre`, `rsga` and `the_weekly` are partly implemented, have stub functions, or are commented out in the download script.
- `three_day_forecast` filenames carry a 12-character timestamp; the other reports use 8 characters.
- `three_day_forecast` (`get_three_day_forecast` → `three_day_forecast_3day_3hr_Kp.csv`) has two reports a day, 0030 and 1230, so it uses `fill_nans_func(freq='12h', slots=...)`.
  - Each report is placed in the slot from its **filename**, not its header, because a few 1230 reports were issued late (00:20 the next day).
  - `Forecast Issued` still holds the header time. Tables start on the issue day, so `Start Offset (hr)` is about −0.5 or −12.5.
  - Files in `THREE_DAY_FORECAST_EXCLUDED_FILES` are skipped as if they did not exist, so their slots come out as missing reports. The list holds `202510071230` (contains Kp 3.37, an invalid value) and three `…0030` files whose headers mistype the issue time as ~12:25. Add new bad files there.
  - Files that are exact copies of an earlier report (same issue time and values) are dropped by `drop_repeated_reports`, leaving their slot empty.
  - Kp is in whole numbers for tables starting up to 2022-11-14, and in thirds after that.
  - `scripts/extract_forecasts.py` converts it to `three_day_forecast_3day_3hr_ap.csv` with `convert_Kp_forecast_to_ap`. Any invalid Kp in a new report makes the conversion raise, so exclude that file.

**Testing convention:** utils functions take a `test` argument.
- In `extract_forecasts_utils` and `create_baseline_forecasts_utils`, passing a directory path as `test` sends output there instead of the real output dir, and tests pass a `tempfile.TemporaryDirectory`. When reading inputs, a truthy `test` switches to fixtures in `testing/resources/testing_files/`.
- Expected DataFrames live in `testing/resources/testing_resources.py`.
- The baseline-forecast tests read the committed real `extracted_data/*.csv`, so they check specific historical values.
- In `make_calanders_utils.create_daily_calander_plot`, passing a directory as `test` both saves there and reads fixtures from `testing/resources/testing_files/`.
