# Impact of Fuel Prices and Metro Fares on Metro Ridership in Istanbul (2013–2024)

## Research question
Do fuel prices, metro fares and car sales explain annual metro ridership in Istanbul?
Hypotheses (one-sided, alpha = 0.05):
- H1: higher fuel prices -> higher ridership
- H2: higher fares -> lower ridership
- H3: higher car sales -> lower ridership
For H2 and H3 a *positive* correlation is evidence against the alternative, so the correct
conclusion is "fail to reject H0" (one-sided p close to 1), not a significant effect.

## Data and preparation
- Ridership: Metro Istanbul / IBB annual passengers. Fuel: Aytemiz/TPPD unleaded petrol price changes.
  Fares: IBB Istanbulkart full fare. Car sales: ODMD (Turkey-wide, not Istanbul-only).
- Yearly prices are **time-weighted** (each price counts for the number of days it was in force),
  not the plain mean of the rows in the file. The 2013 fare only covers 28 Jun–31 Dec.
- Prices are deflated with Turkish CPI (World Bank WDI FP.CPI.TOTL.ZG, chained, 2013 = 100)
  to get real prices.

## Key methodological change: nominal vs. real prices
Nominal fuel and fare prices rose ~9x and ~10x between 2013 and 2024 because of inflation, and
ridership also trended upward, so any two trending series correlate. This is a spurious-correlation risk.

| Test (n = 12 unless noted) | Fuel | Fare | Car sales |
|---|---|---|---|
| Nominal levels, Pearson r | 0.79 (p = 0.002) | 0.79 (p = 0.002) | -0.03 (p = 0.92) |
| **Real levels**, Pearson r | 0.22 (p = 0.50) | -0.16 (p = 0.62) | – |
| Year-over-year log change (n = 11), r | 0.65 (one-sided p = 0.015) | -0.36 (p = 0.14) | -0.52 (p = 0.050) |

Regression ln(ridership) ~ ln(real fuel) + ln(real fare) + trend + COVID dummy (2020–21), R² = 0.97, 7 residual df:
fuel -0.43 (p = 0.066), fare -0.16 (p = 0.50), trend +6.1%/yr (p < 0.001), COVID -0.68 (p < 0.001).

## Results
- The strong positive nominal correlations of the first version are **mostly explained by shared
  inflation and the long-run upward trend**; they disappear with real prices.
- The only signal that survives is the year-over-year fuel-price change (r = 0.65), but it is not
  robust: it is not significant with Spearman correlation (p = 0.10), and in the multivariate model
  with trend and COVID the real fuel coefficient is negative and not significant.
- No evidence that fares reduce ridership (H2) and weak, borderline evidence for car sales (H3).
- With 11–12 annual observations none of these are causal estimates.

## Forecast validation
The original R² of 0.80–0.82 came from a random 80/20 split of only 9 rows (2 test rows), which is not meaningful.
Honest validation: one-year-ahead expanding window, 2018–2024:

| Model | RMSE (M passengers) | MAPE |
|---|---|---|
| Naive (last year's value) | 174 | 25.0% |
| Linear trend only | 194 | 28.3% |
| XGBoost (real prices) | 198 | 28.3% |
| Random forest (real prices) | 200 | 29.6% |
| Linear (real prices + trend) | 337 | 39.8% |

No model beats the naive baseline, largely because of the COVID collapse in 2020. Tree models also cannot
extrapolate beyond the training range, so the 2025 scenario forecasts were removed. (The earlier
forecast also fed a fare of 5.25 TL, far below the 2024 value of ~18.9 TL, and the "what-if" scenarios were
identical because the trees ignored the changed inputs.)

## Limitations
- 12 annual points; few degrees of freedom; COVID outlier years.
- Fuel is national pricing, ridership is Istanbul-only; car sales are national.
- Fares and fuel prices are collinear (r = 0.58 in real terms).
- Ridership series may be affected by network expansion (new lines), which is not controlled for.
- Population data was left out because the file is not in the repository.

## Conclusion
After adjusting for inflation and trend, this data does **not** support the claim that fare level is the
main driver of ridership or that fuel prices strongly raise it. Ridership growth is mainly a time
trend (network expansion, population growth) interrupted by COVID. Monthly data and network-length
controls are the natural next steps.
