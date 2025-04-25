# Impact-of-Fuel-Prices-and-Metro-Fares-on-Public-Transport-Usage-in-Istanbul

## Project Overview
This project explores the relationship between fuel prices, metro fares, vehicle sales, and public transport usage in Istanbul over the years. By analyzing these factors, I aim to determine their impact on metro ridership trends, providing insights that policymakers can use to encourage public transportation usage.

---

## Motivation

As someone who lives in Istanbul and uses the metro regularly, I’ve always been curious about how different factors, like fuel prices and metro fares, affect public transportation usage. While I was in the Netherlands, I learned that when fuel prices rise, the government sometimes lowers public transport fares to encourage more people to use it. This made me wonder if similar trends exist in Istanbul. This study gives me a chance to analyze a real-world issue while improving my data analysis skills through visualization, statistical analysis, and modeling.

---
## Hypothesis
- Null Hypothesis 1 (H₀₁): Fuel prices do not have a significant impact on metro ridership in Istanbul.
- Alternative Hypothesis 1 (H₁₁): Increases in fuel prices lead to higher metro ridership in Istanbul.
- Null Hypothesis 2 (H₀₂): Metro fare changes do not significantly affect metro ridership in Istanbul.
- Alternative Hypothesis 2 (H₁₂): Metro fare increases lead to lower metro ridership in Istanbul.
- Null Hypothesis 3 (H₀₃): Vehicle sales do not have a significant impact on metro ridership.
- Alternative Hypothesis 3 (H₁₃): Increases in vehicle sales lead to a decline in metro ridership as more people opt for private transportation.

---

## Data Sources
To conduct this analysis, the project will utilize:
- Metro Ridership Data: Yearly metro passenger counts and trip frequencies from official transport source IBB Metro Istanbul: "Yolcu Istatikleri".
- Fuel Price Data: Yearly historical fuel prices in Turkey from Aytemiz "Arşiv Akaryakıt ve LPG Pompa Fiyatları" and from TPPD "GEÇMİŞ DÖNEM AKARYAKIT FİYATLARI".
- Metro Fare Data: Yearly metro ticket prices for full, student, and discounted categories from tuhim.ibb.gov.tr .
- Vehicle Sales Data: Yearly automobile vehicle sales in Turkey, sourced from official automotive market reports. (Otomotiv Distribütörleri ve Mobilite Derneği | ODMD)

---

## Planned Analysis
Once I have the data, I'll analyze how metro ridership changes in response to fuel price fluctuations, fare adjustments, and vehicle sales. Here’s how I plan to approach it:

- Looking for patterns in metro usage when fuel prices rise or fall.
- Comparing ridership in years with high and low fuel prices to see if people change their public transport habits.
- Examining whether an increase in car sales leads to a drop in metro usage.
- Using regression analysis to understand if fuel prices, metro fares, and vehicle sales have a predictable impact on metro ridership.
I’ll finalize the exact methods after reviewing the data to make sure it's complete and suitable for analysis.
---

## Expected Outcomes
- If fuel prices increase, metro ridership is expected to rise as people look for cost-effective alternatives to driving.
- If metro fares increase, ridership may decrease, especially among full-fare passengers, while students and discounted fare users might be less affected.
- If car sales rise, metro usage may decline, indicating a shift toward private vehicle ownership.
- The combined effect of fuel prices, metro fares, and car sales could reveal key trends in transportation choices over time.

---

## EDA Process
I began the EDA process by collecting all relevant datasets. Some of the data were available on a monthly basis, so I aggregated them into annual values by summing monthly figures and calculating their averages to better represent each year.
In cases where annual data were missing (e.g., Istanbulkart prices for certain years like 2013), I assumed no changes had occurred and used the previous year's data. This situation only applied to a small number of cases.
After assembling the datasets, I cleaned them by removing unnecessary columns and handling inconsistencies. Once the data was properly prepared, I proceeded to the visualization phase to gain further insights.

---

## Visualization Stage
In the visualization phase, I explored the relationships between metro ridership and various external factors such as fuel prices, public transport fares, and car sales.

1) Fuel Price vs Metro Ridership: A positive correlation was observed between fuel prices and metro usage. As fuel prices increased, metro ridership generally followed an upward trend, suggesting a potential shift from private vehicles to public transport in response to rising fuel costs.
2) Metro Fare vs Metro Ridership: Interestingly, even though metro fares increased significantly in recent years, ridership also showed an upward trend. This may indicate that fare hikes did not deter passengers, possibly due to limited transportation alternatives or overall inflation effects.
3) Car Sales vs Metro Ridership: Unlike the other two, the correlation between car sales and metro ridership was weak and slightly negative. This implies that car ownership trends may not directly influence public transportation use on a macro scale.
4) Correlation Heatmap: A correlation matrix was generated to understand the relationships between all variables. As expected, various fare types and fuel categories showed high mutual correlation. However, metro ridership showed relatively low correlation with these financial indicators, reinforcing the complexity of ridership behavior.
5) Time Series Visualization: I also plotted trends over time to highlight how fuel prices, metro fares, and passenger numbers evolved from 2013 to 2024. While fuel prices and fares rose steadily, ridership had a dip during the COVID-19 period and then continued to rise sharply afterward.

---

## Hypothesis Testing

To examine the statistical significance of observed relationships, hypothesis testing was conducted using Pearson correlation and linear regression. The significance level was set to 0.05.

---

### Hypothesis 1: Fuel Price - Metro Ridership

- **Pearson's r**: 0.789  
- **p-value**: 0.0023  
- **Regression Slope**: 11,709,814.91  
- **Relationship Direction**: Positive  
- **Conclusion**: Reject H01 (Significant)

Interpretation: There is a strong, statistically significant positive relationship between fuel prices and metro ridership. As fuel prices increase, metro usage tends to increase as well.

---

### Hypothesis 2: Metro Fare - Metro Ridership

- **Pearson's r**: 0.788  
- **p-value**: 0.0023  
- **Regression Slope**: 23,288,328.18  
- **Relationship Direction**: Positive  
- **Conclusion**: Fail to Reject H02

Interpretation: Although the correlation is statistically significant, the positive relationship is counterintuitive. It may suggest that fare increases did not deter ridership due to external factors like inflation, lack of alternatives, or population growth.

---

### Hypothesis 3: Vehicle Sales - Metro Ridership

- **Pearson's r**: -0.032  
- **p-value**: 0.9206  
- **Regression Slope**: -47.23  
- **Relationship Direction**: Negative (but negligible)  
- **Conclusion**: Fail to Reject H03

Interpretation: There is no significant relationship between vehicle sales and metro ridership. Car ownership trends do not appear to have a meaningful impact on public transport usage.




