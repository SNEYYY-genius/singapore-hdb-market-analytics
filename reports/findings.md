# Singapore HDB Resale Market — Key Findings

## 1. Market Overview

The dataset contains 239,330 HDB resale transactions across 26 Singapore towns from January 2017 to August 2026, representing approximately S$127.9 billion in total transaction value.

The median resale price was S$502,000, while the median price per square metre was S$5,307.69.

### Transaction Activity

Transaction volume increased gradually from 20,509 transactions in 2017 to 23,333 in 2020.

Activity increased sharply in 2021, reaching 29,087 transactions — approximately 24.7% higher than 2020 and the highest annual volume in the dataset.

Transaction activity subsequently moderated in 2022 and 2023 before increasing again to 27,832 transactions in 2024.

The 2026 transaction count should not be directly compared with previous full years because the dataset currently covers only January to August 2026.

### Initial Business Interpretation

The market overview indicates substantial transaction activity but also meaningful variation over time. Further analysis should investigate whether market activity and price growth are concentrated in particular towns and property segments.

## 2. Town Performance

### Transaction Activity

SENGKANG recorded the largest number of resale transactions over the study period, followed by PUNGGOL and WOODLANDS.

Together, the leading towns account for a substantial share of resale activity, indicating that transaction volume is geographically concentrated.

### Price Levels

BUKIT TIMAH had the highest median resale price, while CENTRAL AREA had the highest median price per square metre.

The difference between absolute price and price per sqm indicates that property size and market location should be considered separately when comparing towns.

### Transaction Value

SENGKANG represented the largest aggregate resale transaction value over the study period, reflecting a combination of transaction volume and property prices.

## 3. Segment Analysis

### Most Active Segments

SENGKANG(4 ROOM) recorded the highest number of resale transactions, followed by PUNGGOL(4 ROOM) and YISHUN(4 ROOM).

This indicates that resale activity is concentrated not only geographically, but also within particular flat types.

### Price Differences

The highest median resale prices were concentrated in QUEENSTOWN(EXECUTIVE), while the highest median price-per-sqm segments were CENTRAL AREA(5 ROOM).

The difference between total price and price per sqm suggests that property size and location affect segment rankings differently.

### Commercial Interpretation

High-volume Town × Flat Type segments may represent priority markets for property listings, mortgage referrals, or customer acquisition because they combine geographic concentration with substantial transaction activity.

## 4. Growth Analysis

### 2025 Price Growth

Median resale price per sqm increased substantially in several towns in 2025.
Queenstown recorded the strongest growth at 25.10%, followed by Toa Payoh
at 18.32% and Central Area at 11.80%.

However, strong price growth did not necessarily correspond with increasing
transaction activity.

### Price and Transaction Momentum

Only three towns recorded simultaneous growth in both median price per sqm
and transaction volume in 2025:

- Toa Payoh: +18.32% price/sqm growth and +31.56% transaction growth
- Sembawang: +10.50% price/sqm growth and +17.92% transaction growth
- Marine Parade: +7.58% price/sqm growth and +14.08% transaction growth

Toa Payoh showed the strongest combined momentum, with substantial increases
in both pricing and transaction activity.

These results suggest that market momentum varied considerably across towns.
Price appreciation alone does not necessarily indicate increasing transaction
activity, highlighting the importance of evaluating both pricing and market
volume when assessing local HDB resale conditions.
## 5. Exploratory Market Analysis

### Market Evolution

HDB resale transaction activity increased gradually between 2017 and 2020 before reaching a dataset peak in 2021. Transaction volumes subsequently moderated, with a temporary rebound in 2024.

Monthly transaction activity was considerably more volatile, including a sharp temporary decline around 2020 followed by a strong recovery.

### Resale Price Trends

Pricing followed a clearer long-term upward trend. Median resale prices were broadly stable between 2017 and 2019 before increasing substantially from 2020 onward, reaching approximately S$628,000 in 2025.

Median price per square metre followed a similar pattern, increasing from approximately S$4,200–4,300 per sqm during 2017–2019 to around S$6,500 per sqm in 2025.

The simultaneous increase in both absolute resale prices and standardized price per sqm suggests that the upward trend was not driven solely by differences in flat size.

### Largest HDB Resale Markets

Sengkang recorded the highest resale transaction volume and aggregate transaction value over the study period, followed by other large markets including Punggol, Tampines, Woodlands and Yishun.

Town rankings differed when comparing transaction volume with transaction value. For example, Tampines ranked higher by transaction value than by volume, while Bukit Merah entered the top ten by transaction value despite lower transaction volume.

This demonstrates that transaction count and market value capture different dimensions of commercial opportunity.

### Premium Markets

Central Area, Queenstown, Bukit Merah and Bukit Timah recorded some of the highest median resale prices per square metre.

These premium-price markets differ considerably from high-volume markets such as Sengkang and Punggol, highlighting the importance of distinguishing market size from pricing level.

### Recent Market Momentum

Queenstown recorded the strongest 2025 median price-per-sqm growth at 25.10%, while Toa Payoh increased by 18.32%.

However, price appreciation did not necessarily coincide with increasing transaction activity.

Toa Payoh stood out with both 18.32% price-per-sqm growth and 31.56% transaction growth, while Sembawang and Marine Parade also recorded simultaneous positive growth across both indicators.
## 6. Property Characteristics and Resale Prices

### Floor Area

Floor area showed the strongest simple numerical relationship with resale price, with a correlation of approximately 0.56.

Median resale prices increased substantially across floor-area bands, from roughly S$310,000 for units below 60 sqm to more than S$800,000 for units above 150 sqm. However, considerable price variation remained within similar floor sizes, indicating that size alone does not explain resale value.

### Remaining Lease

Remaining lease showed a positive correlation of approximately 0.30 with resale price. Flats with shorter remaining leases generally recorded lower median transaction prices, while units with longer leases tended to command higher prices.

The relationship was not perfectly monotonic across all lease bands, suggesting that other factors such as location, flat type, and transaction composition also influence prices.

### Storey

Storey midpoint had a positive correlation of approximately 0.34 with resale price. Higher-storey groups generally recorded higher median transaction prices.

However, this descriptive relationship may partly reflect differences in location, flat type, building age, and other property characteristics.

### Location

Substantial price differences were observed across towns. Bukit Timah, Bishan, Queenstown and Bukit Merah recorded some of the highest median absolute resale prices, reinforcing the importance of location in HDB market pricing.

### Flat Type

Median resale prices increased substantially across larger flat types. Multi-Generation and Executive units recorded the highest median prices, followed by 5-room and 4-room units.

This relationship partly reflects differences in floor area and other property characteristics.

### Correlation Summary

Among the continuous variables examined, floor area had the strongest positive correlation with resale price (0.56), followed by storey midpoint (0.34) and remaining lease (0.30). Flat age was negatively correlated with resale price (-0.30).

Remaining lease and flat age were almost perfectly negatively correlated (-0.9996), indicating that they contain highly overlapping information. Therefore, both variables should not be included simultaneously in the subsequent regression model.

## 7. Regression Analysis

A multivariate OLS regression was used to examine HDB resale-price differences while controlling for floor area, remaining lease, storey, town, flat type, and transaction year. Robust HC3 standard errors were used.

The model achieved an adjusted R-squared of 0.907, indicating that the included observed characteristics explain approximately 90.7% of the variation in log resale prices in the dataset.

### Continuous Property Characteristics

Holding the other included characteristics constant:

- Each additional square metre of floor area was associated with approximately 0.84% higher resale price.
- Each additional year of remaining lease was associated with approximately 1.03% higher resale price.
- Each additional storey level was associated with approximately 0.79% higher resale price.

A robustness model using price per square metre produced nearly identical estimates for remaining lease and storey, suggesting that these relationships were not driven solely by differences in flat size.

### Location Effects

Using Ang Mo Kio as the reference town, Bukit Timah showed the largest conditional price premium at approximately 35.0%, followed by Central Area at 29.7% and Marine Parade at 28.2%.

This indicates substantial location-related price differences even after controlling for measured property characteristics and transaction year.

### Flat-Type Effects

Using 1-room flats as the reference category, Multi-Generation and Executive flats showed the largest conditional price premiums at approximately 61.6% and 50.3%, respectively.

Even after controlling for floor area, flat type remained strongly associated with resale-price differences.

### Interpretation and Limitations

The regression results represent conditional associations rather than causal effects. The model does not directly account for factors such as exact MRT distance, nearby amenities, renovation quality, orientation, view, or block-specific characteristics.

## 8. Market Segmentation
- The dataset contains 239,330 transactions from January 2017 through August 2026. Both 2024 and 2025 have all 12 observed months. Historical summaries include partial-year 2026; growth compares only 2025 with 2024.
- There are 131 Town × Flat Type segments. The 500 historical / 30 per comparison-year screen retains 85. Annual thresholds of 20, 30, and 50 all retain the same 85 segments and 19 positive-momentum segments.
- Sengkang × 4 Room leads historical transaction count (9,666), followed by Punggol × 4 Room (9,170). These also lead cumulative transaction value at approximately S$4.996 billion and S$4.991 billion.
- Central Area × 5 Room has the highest historical median price per sqm (S$9,904.76), followed by Central Area × 4 Room (S$9,293.04).
- Tampines × 4 Room records +6.86% median price-per-sqm growth and +2.88% transaction growth. Toa Payoh × 4 Room records +12.90% and +41.47%, respectively; Sembawang × 5 Room records +8.18% and +26.95%.
- Large median price changes coincide with changes in sale composition: Central Area × 4 Room's median remaining lease rises from 77.17 to 84.33 years; Clementi × 4 Room's from 59.50 to 87.00 years; Clementi × 5 Room's from 59.50 to 78.54 years, with median storey rising from 8 to 14. These observations support investigating composition rather than assuming same-property appreciation. They do not quantify causal contributions.

## 9. Opportunity Analysis

### Method

A volume-growth matrix classified 85 eligible Town × Flat Type segments using 2025 transaction counts and 2025 versus 2024 transaction growth. Large segments had at least 209 transactions, the eligible-segment median. Positive growth meant strictly above zero. Bubble area represented 2025 transaction value and colour represented median price-per-sqm growth.

Eligibility required at least 500 historical transactions and 30 transactions in each comparison year. Historical eligibility uses January 2017–August 2026, making this a retrospective analysis rather than an as-of-2025 backtest. The eligible segments account for 95.6% of 2025 transactions in the dataset.

### Classification results

| Category | Segments | Interpretation |
|---|---:|---|
| Priority | 9 | Larger segments with growing transaction activity |
| Emerging | 11 | Smaller segments with growing transaction activity |
| Established | 35 | Larger segments with flat or declining transaction activity |
| Lower Priority | 30 | Smaller segments with flat or declining transaction activity |

The nine Priority segments recorded 4,036 transactions and approximately S$2.737 billion in transaction value in 2025. Their aggregate volume grew 10.33%, while total dataset volume declined 9.87%.

### Priority research candidates

- Tampines × 4 Room had the largest 2025 volume within Priority: 892 transactions, +2.88% transaction growth and +6.86% median price-per-sqm growth.
- Sembawang × 4 Room recorded 545 transactions, +12.37% transaction growth and +8.70% price-per-sqm growth.
- Toa Payoh × 4 Room recorded 423 transactions, +41.47% transaction growth and +12.90% price-per-sqm growth.
- Sembawang × 5 Room recorded 325 transactions, +26.95% transaction growth and +8.18% price-per-sqm growth.
- Tampines × 5 Room qualifies on size and positive growth, but its +0.59% activity growth should be described as approximately stable rather than strong momentum.

### Robustness and interpretation

Changing the size cutoff to the 40th, 50th and 60th percentiles produced 10, 9 and 8 Priority segments. Eight remained Priority throughout: Tampines × 4 Room, Sembawang × 4 Room, Tampines × 5 Room, Toa Payoh × 3 Room, Toa Payoh × 4 Room, Bukit Panjang × 4 Room, Hougang × 3 Room and Sembawang × 5 Room.

Clementi × 4 Room sits exactly at the baseline 209-transaction size boundary and leaves Priority under the stricter cutoff. Its large median price increase coincides with a shift toward longer remaining leases in Step 17's composition check.

There are 20 activity-growing segments across Priority and Emerging, compared with 19 segments showing both positive activity and positive price growth. The difference is Geylang × 5 Room: transaction growth was +16.39% while median price-per-sqm growth was -0.27%.

These categories prioritize commercial research; they do not forecast investment returns, agency revenue or profitability. Median price changes can reflect the mix of properties sold. Large Established segments still account for 63.47% of eligible 2025 transactions and should not be ignored simply because activity declined.
