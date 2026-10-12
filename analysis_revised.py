"""
Revised analysis: fuel prices, metro fares, vehicle sales and Istanbul metro ridership (2013-2024).

What changed compared with main.py / XGBoost.py / randomForest.py
  1. Prices are converted to REAL (inflation-adjusted) TL using annual-average CPI inflation.
  2. Yearly fuel and fare prices are TIME-WEIGHTED (price in force each day), not a plain mean of
     the rows in the price list.
  3. Hypotheses are tested on levels AND on year-over-year log changes, and in a regression that
     controls for a time trend and COVID years.  One-sided p-values match the one-sided hypotheses.
  4. ML models are validated one year ahead (expanding window) and leave-one-year-out, and are
     compared against naive baselines.  No 2025 point forecast is produced (see notes in output).

CPI source: World Bank WDI, "Inflation, consumer prices (annual %)" (FP.CPI.TOTL.ZG) for Turkiye,
which is derived from TUIK CPI annual averages.  Last updated 2026-10-08.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import statsmodels.formula.api as smf
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "csv"
OUT = ROOT / "revised_output"
OUT.mkdir(exist_ok=True)
YEARS = list(range(2013, 2025))
FUEL_COL = "KURŞUNSUZ BENZİN (TL/LT)"

# Annual-average CPI inflation, % (World Bank WDI / TUIK), used to build a 2013 = 100 index
INFLATION = {2013: 7.49308913314732, 2014: 8.8545718967802, 2015: 7.67085521554052,
             2016: 7.7751335303658, 2017: 11.1443085201022, 2018: 16.3324781477783,
             2019: 15.176809642769, 2020: 12.2789597724893, 2021: 19.5964927532842,
             2022: 72.3088300496956, 2023: 53.8594084019764, 2024: 58.5064492168435}
cpi = {2013: 100.0}
for y in YEARS[1:]:
    cpi[y] = cpi[y - 1] * (1 + INFLATION[y] / 100)

log = []
def say(s=""):
    print(s)
    log.append(s)

# ------------------------------------------------------------------ data
TR_MONTHS = {"Oca": 1, "Şub": 2, "Mar": 3, "Nis": 4, "May": 5, "Haz": 6,
             "Tem": 7, "Ağu": 8, "Eyl": 9, "Eki": 10, "Kas": 11, "Ara": 12}

def parse_tr_date(s):
    d, m, y = str(s).strip().split(".")
    return pd.Timestamp(year=2000 + int(y), month=TR_MONTHS[m], day=int(d))

def daily_step_series(dates, values, end="2024-12-31"):
    s = pd.Series(values, index=pd.DatetimeIndex(dates)).sort_index()
    s = s[~s.index.duplicated(keep="last")]
    idx = pd.date_range(s.index.min(), end, freq="D")
    return s.reindex(idx).ffill()

def yearly_time_weighted(daily):
    return daily.groupby(daily.index.year).mean().reindex(YEARS)

# fuel (price list rows -> daily step function -> yearly time-weighted mean)
fuel_raw = pd.read_csv(CSV / "Benzin.csv", sep=";").dropna(subset=["DATE"])
fuel_raw["d"] = fuel_raw["DATE"].map(parse_tr_date)
fuel_raw["p"] = fuel_raw[FUEL_COL].astype(str).str.strip().str.replace(",", ".").astype(float)
fuel_tw = yearly_time_weighted(daily_step_series(fuel_raw["d"], fuel_raw["p"].values))

# fare (fare-change dates -> daily step function; 2013 covers 28 Jun - 31 Dec only)
fare_raw = pd.read_csv(CSV / "Istanbulkart_fare.csv", sep=";", encoding="utf-8-sig")
fare_raw["d"] = pd.to_datetime(fare_raw["Date"], dayfirst=True)
fare_raw["p"] = fare_raw["Full Istanbulkart"].astype(str).str.replace(",", ".").astype(float)
fare_tw = yearly_time_weighted(daily_step_series(fare_raw["d"], fare_raw["p"].values))

# ridership, car sales, and the original (unweighted) yearly files for comparison
pas = pd.read_csv(CSV / "passenger_data.csv", sep=";", encoding="utf-8-sig")
pas["passenger"] = pas["passenger"].str.replace(".", "", regex=False).astype(int)
pas = pas.set_index("Year")["passenger"]
car = pd.read_csv(CSV / "car_sales_data.csv").set_index("Year")["Total"]
fuel_old = pd.read_csv(CSV / "fuel_price_data.csv")
fuel_old = fuel_old.assign(Year=fuel_old["YIL"].astype(int)).set_index("Year")[FUEL_COL]
fare_old = pd.read_csv(CSV / "Istanbulkart_Fare_Avg.csv").set_index("Year")["Full Istanbulkart"]

df = pd.DataFrame({
    "ridership": pas.reindex(YEARS),
    "fuel_nom": fuel_tw, "fare_nom": fare_tw, "cars": car.reindex(YEARS),
    "fuel_old": fuel_old.reindex(YEARS), "fare_old": fare_old.reindex(YEARS),
})
df["cpi"] = pd.Series(cpi)
df["fuel_real"] = df["fuel_nom"] / df["cpi"] * 100
df["fare_real"] = df["fare_nom"] / df["cpi"] * 100
df["trend"] = df.index - 2013
df["covid"] = df.index.isin([2020, 2021]).astype(int)
df["ridership_m"] = df["ridership"] / 1e6
df.round(3).to_csv(OUT / "annual_dataset.csv")

say("=" * 70)
say("DATA CHECK (n = %d years, %d-%d)" % (len(df), YEARS[0], YEARS[-1]))
say("=" * 70)
say(df[["ridership_m", "fuel_old", "fuel_nom", "fare_old", "fare_nom", "cpi",
        "fuel_real", "fare_real"]].round(2).to_string())
say("fuel_old / fare_old = original yearly files (plain mean of rows); *_nom = time-weighted.")
say("*_real = nominal / CPI * 100 (2013 TL).  2013 fare covers 28 Jun - 31 Dec only.")

# ------------------------------------------------------------------ hypothesis tests
def one_sided_p(r, p_two, direction):
    """direction = +1 for 'positive effect', -1 for 'negative effect'."""
    return p_two / 2 if np.sign(r) == direction else 1 - p_two / 2

def corr_row(label, x, y, direction):
    r, p = pearsonr(x, y)
    rho, p_s = spearmanr(x, y)
    return (label, len(x), r, p, one_sided_p(r, p, direction), rho, p_s)

def show(rows, title):
    say("\n" + title)
    say(f"{'test':34s} {'n':>3s} {'r':>7s} {'p(2-sided)':>11s} {'p(1-sided)':>11s} {'spearman':>9s} {'p':>7s}")
    for lab, n, r, p, p1, rho, ps in rows:
        say(f"{lab:34s} {n:3d} {r:7.3f} {p:11.4f} {p1:11.4f} {rho:9.3f} {ps:7.3f}")

D = {"fuel": +1, "fare": -1, "cars": -1}   # direction claimed by each alternative hypothesis
say("\n" + "=" * 70)
say("HYPOTHESIS TESTS (one-sided alternatives: fuel +, fare -, car sales -)")
say("=" * 70)

show([corr_row("A. original files, nominal: fuel", df.fuel_old, df.ridership, +1),
      corr_row("A. original files, nominal: fare", df.fare_old, df.ridership, -1),
      corr_row("A. nominal: car sales", df.cars, df.ridership, -1)],
     "A. Levels, nominal prices (reproduces the README)")
show([corr_row("B. time-weighted nominal: fuel", df.fuel_nom, df.ridership, +1),
      corr_row("B. time-weighted nominal: fare", df.fare_nom, df.ridership, -1)],
     "B. Levels, nominal but time-weighted yearly prices")
show([corr_row("C. real: fuel", df.fuel_real, df.ridership, +1),
      corr_row("C. real: fare", df.fare_real, df.ridership, -1)],
     "C. Levels, REAL (inflation-adjusted) prices")

lg = np.log(df[["ridership", "fuel_real", "fare_real", "cars", "fuel_nom", "fare_nom"]]).diff().dropna()
show([corr_row("D. d ln real fuel", lg.fuel_real, lg.ridership, +1),
      corr_row("D. d ln real fare", lg.fare_real, lg.ridership, -1),
      corr_row("D. d ln car sales", lg.cars, lg.ridership, -1),
      corr_row("D. d ln nominal fuel (for contrast)", lg.fuel_nom, lg.ridership, +1)],
     "D. Year-over-year log changes (removes shared trends; n = 11)")

say("\nE. Regression: ln(ridership) ~ ln(real fuel) + ln(real fare) + trend + COVID(2020-21)")
dfl = df.assign(l_rid=np.log(df.ridership), l_fuel=np.log(df.fuel_real), l_fare=np.log(df.fare_real))
ols = smf.ols("l_rid ~ l_fuel + l_fare + trend + covid", data=dfl).fit()
say(ols.summary2().tables[1].round(3).to_string())
say(f"R2 = {ols.rsquared:.3f}, adj R2 = {ols.rsquared_adj:.3f}, n = {int(ols.nobs)}, residual df = {int(ols.df_resid)}")
say(f"corr(ln real fuel, ln real fare) = {dfl.l_fuel.corr(dfl.l_fare):.2f} (collinearity makes separate effects hard to identify)")
say("Note: with 12 annual points, coefficients are exploratory, not causal estimates.")

# ------------------------------------------------------------------ forecasting validation
say("\n" + "=" * 70)
say("FORECAST VALIDATION (ridership in millions)")
say("=" * 70)
feat_prices = ["fuel_real", "fare_real"]
feat_trend = ["fuel_real", "fare_real", "trend"]

def make_models():
    return {
        "RandomForest (real prices)": (lambda: RandomForestRegressor(n_estimators=300, random_state=42), feat_prices),
        "XGBoost (real prices)": (lambda: XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=2, random_state=42), feat_prices),
        "Linear (real prices + trend)": (lambda: LinearRegression(), feat_trend),
        "Linear trend only": (lambda: LinearRegression(), ["trend"]),
    }

def evaluate(split_years, train_rule):
    res = {}
    y_all = df.ridership_m
    for name, (mk, cols) in make_models().items():
        preds = []
        for t in split_years:
            tr = train_rule(t)
            m = mk().fit(df.loc[tr, cols], y_all[tr])
            preds.append(float(m.predict(df.loc[[t], cols])[0]))
        res[name] = np.array(preds)
    res["Naive: last year's value"] = np.array([y_all[t - 1] for t in split_years])
    actual = y_all[split_years].values
    rows = []
    for name, p in res.items():
        rmse = float(np.sqrt(np.mean((p - actual) ** 2)))
        mape = float(np.mean(np.abs(p - actual) / actual) * 100)
        rows.append((name, rmse, mape))
    return pd.DataFrame(rows, columns=["model", "RMSE (M)", "MAPE (%)"]).sort_values("RMSE (M)").round(1)

fwd_years = [y for y in YEARS if y >= 2018]          # train on all earlier years (>= 5 points)
say("\nOne-year-ahead, expanding window (predict %d-%d; each year uses only earlier years):" % (fwd_years[0], fwd_years[-1]))
tab_fwd = evaluate(fwd_years, lambda t: [y for y in YEARS if y < t])
say(tab_fwd.to_string(index=False))

loyo_years = YEARS
say("\nLeave-one-year-out (all 12 years; optimistic because future years help predict past years):")
tab_loyo = evaluate([y for y in loyo_years if y > 2013],
                    lambda t: [y for y in YEARS if y != t])
say(tab_loyo.to_string(index=False))

say("\nOriginal setup for comparison: README/report R2 of 0.80-0.82 came from a random 80/20 split")
say("of the rows that survive the merge.  Fares were not forward-filled in the ML scripts, so")
n_ml_rows = 9
say(f"only {n_ml_rows} years (2013, 2014, 2016, 2017, 2020-2024) remain and the test set has 2 rows;")
say("R2 on 2 points is not a meaningful performance estimate.")

# ------------------------------------------------------------------ figure
idx = df[["ridership", "fuel_nom", "fuel_real"]].div(df[["ridership", "fuel_nom", "fuel_real"]].iloc[0]) * 100
fig, ax = plt.subplots(figsize=(8.5, 4.8))
ax.plot(idx.index, idx.ridership, marker="o", lw=2.4, color="#1f4e9e", label="Metro ridership")
ax.plot(idx.index, idx.fuel_nom, marker="s", lw=2, color="#c0392b", label="Gasoline price, nominal TL")
ax.plot(idx.index, idx.fuel_real, marker="^", lw=2, color="#2e8b57", label="Gasoline price, real TL (CPI-adjusted)")
ax.set_yscale("log")
ax.set_ylabel("Index, 2013 = 100 (log scale)")
ax.set_title("Nominal fuel prices rose ~9x, real fuel prices did not")
ax.grid(alpha=0.3, which="both")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT / "nominal_vs_real_fuel.png", dpi=160)

(OUT / "results.txt").write_text("\n".join(log), encoding="utf-8")
print("\nSaved:", OUT)
