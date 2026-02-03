#import "@preview/hei-synd-report:0.1.1": *
#import "/metadata.typ": *
#pagebreak()

= Method

/*== Libraries used
//#rocketbox()[NumPy, KaggleHub, YFinance and Pandas are directly handled by the Dataset class]
- NumPy: array manipulation
- Pandas: dataset (dataframe) manipulation
- MatPlotLib: plotting graphs on the screen
- Seaborn: extends MatPlotLib in order to draw correlation matrices
- SciPy: base package for every Scikit libraries
- Scikit-Learn: toolkit used to scale our dataset and to use some metrics during tests
- StatsForecast: machine learning (used for the AutoARIMA model)
- PyTorch: machine learning (used for the LSTM model)
- UtilsForecast: evaluation of the models
- KaggleHub: data downloader from Kaggle without the need of an API key
//- YFinance: data downloader from Yahoo! Finance
*/

/*These are the version of the libraries used to develop our project:

#raw(lang: "toml", "[dependencies]
python = \">=3.10,<3.11\"
numpy = \">=1.19.5,<2\"
matplotlib = \">=3.5.3,<4\"
scipy = \">=1.9.1,<2\"
seaborn = \">=0.12.2,<0.13\"
kagglehub = \">=0.3.8,<0.4\"
pandas = \">=1.4.4,<2\"
yfinance = \">=0.2.18,<0.3\"
statsforecast = \">=2.0.3,<3\"
utilsforecast = \">=0.2.14,<0.3\"
scikit-learn = \">=1.7.2,<2\"
pytorch = \">=2.9.1,<3\"")
*/

== Sources
The following datasets might be useful to make a conscistent database about logistics.

=== Kaggle
+ #link("https://www.kaggle.com/datasets/datasetengineer/logistics-and-supply-chain-dataset")[Logistics and Supply Chain Dataset] – Focuses on shipment tracking, delivery times, and supply chain efficiency metrics.
+ #link("https://www.kaggle.com/datasets/ayeshaseherr/delivery-logistics-dataset")[Delivery Logistics Dataset] – Contains data on delivery routes, timings, and performance indicators, useful for route optimization and last-mile delivery analysis.
+ #link("https://www.kaggle.com/datasets/nicolemachado/transportation-and-logistics-tracking-dataset")[Transportation and Logistics Tracking Dataset] – Includes real-time tracking data for shipments, ideal for studying transportation efficiency and delays.
+ #link("https://www.kaggle.com/datasets/sujalsuthar/amazon-delivery-dataset")[Amazon Delivery Dataset] – Focuses on last-mile logistics and delivery performance, with insights into delivery times, distances, and customer satisfaction.
+ #link("https://www.kaggle.com/datasets/sezginkaraglle/logistics-dataset")[Logistics Shipment On-Time Delivery Classification Dataset] – Useful for predictive modeling to determine on-time delivery probabilities based on historical data.

/*== Requirements

=== Dataset restrictions
- Due to the high number of tickers, we have only used the crytos with at least 65% of correlation with gold (whatever the method used).
- There is a hole in the dataset downloaded from Kaggle: no data are available *between December 10#super[th] 2024 and January 26#super[th] 2025*. So the data analysis will occur from the first common date with all the interesting tickers and December 9th 2024.
- No cryptocurrency were available before July 17#super[th] 2010 so all dates (from gold dataset) before that moment have been droped

=== Dataset modifications
- In order to use a time series model, the dataset must have its columns renamed:
  + All the dates are in a `ds` column (on a daily basis)
  + Gold values are in a `y` column
  + All exogenous data (cryptocurrency tickers) are normalized
  + Two normalization methods have been used:
    - MinMax scaler from Scikit Learn
    - Mathematical normalization with the following formula: $(X - overline(X)) / sigma_X$

== Dataset

=== Dataset structure
#figure(
  table(
    columns: 5,
    stroke: none,
    align: (left + horizon),
    //inset: 3pt,
    table.hline(stroke: 0.5pt),                         table.vline(x: 0, start: 0, end: 2, stroke: 0.5pt), table.vline(x: 1, start: 0, end: 2, stroke: 0.5pt), table.vline(x: 2, start: 0, end: 2, stroke: 0.5pt), table.vline(x: 3, start: 0, end: 2, stroke: 0.5pt),
    table.vline(x: 4, start: 0, end: 2, stroke: 0.5pt), table.vline(x: 5, start: 0, end: 2, stroke: 0.5pt), table.header(
      [],
      [*date*],
      [*ticker*],
      [*close*],
      [*closeNormalized*],
    ),
    table.hline(stroke: 0.5pt),                         [index],                                            [date],                                             [currency short name],                              [price at closing time in \$],
    [normalized (by ticker) price],                     table.hline(stroke: 0.5pt),
  ),
  caption: "Dataset structure as a Pandas Dataframe",
)

=== Timeseries structure
Time series structure contains exogenous data as follows:
#figure(
  table(
    columns: 4,
    stroke: none,
    align: (left + horizon),
    //inset: 3pt,
    table.hline(stroke: 0.5pt),                         table.vline(x: 0, start: 0, end: 2, stroke: 0.5pt), table.vline(x: 1, start: 0, end: 2, stroke: 0.5pt),              table.vline(x: 2, start: 0, end: 2, stroke: 0.5pt),
    table.vline(x: 3, start: 0, end: 2, stroke: 0.5pt), table.vline(x: 4, start: 0, end: 2, stroke: 0.5pt), table.header(
      [*ds*],
      [*exogenous tickers*],
      [*y*],
      [*unique_id*],
    ),
    table.hline(stroke: 0.5pt),                         [date],                                             [normalized price at closing time (one column for each ticker)], [gold price at closing time (in \$)],
    [XAU],                                              table.hline(stroke: 0.5pt),
  ),
  caption: "Timeseries structure (1/3)",
)
#figure(
  table(
    columns: 3,
    stroke: none,
    align: (left + horizon),
    //inset: 3pt,
    table.hline(stroke: 0.5pt),                         table.vline(x: 0, start: 0, end: 2, stroke: 0.5pt), table.vline(x: 1, start: 0, end: 2, stroke: 0.5pt),
    table.vline(x: 2, start: 0, end: 2, stroke: 0.5pt), table.vline(x: 3, start: 0, end: 2, stroke: 0.5pt), table.header(
      [*day*],
      [*week*],
      [*month*],
    ),
    table.hline(stroke: 0.5pt),                         [day of the month],                                 [week of the year],
    [month of the year],                                table.hline(stroke: 0.5pt),
  ),
  caption: "Timeseries structure (2/3)",
)
#figure(
  table(
    columns: 3,
    stroke: none,
    align: (left + horizon),
    //inset: 3pt,
    table.hline(stroke: 0.5pt),                         table.vline(x: 0, start: 0, end: 2, stroke: 0.5pt), table.vline(x: 1, start: 0, end: 2, stroke: 0.5pt),
    table.vline(x: 2, start: 0, end: 2, stroke: 0.5pt), table.vline(x: 3, start: 0, end: 2, stroke: 0.5pt), table.header(
      [*months_since_start*],
      [*is_holiday*],
      [*days_to_holiday*],
    ),
    table.hline(stroke: 0.5pt),                         [number of month since the first date],             [holiday with respect of US federal calendar],
    [amount of days remaining before next holidays],    table.hline(stroke: 0.5pt),
  ),
  caption: "Timeseries structure (3/3)",
)

=== Tickers

Three different correlation matrices have been computed:
+ *Pearson's correlation matrix* $= bb(E)[((X-overline(X)) dot (Y-overline(Y))) / (sigma_X dot sigma_Y)] = "Cov"(X, Y) / (sigma_X dot sigma_Y)$
+ *Kendall's correlation matrix* $= (("# concordant pairs") - ("# discordent pairs")) / ("# pairs")$
+ *Spearman's correlation matrix* $= "Pearson"("rank"(X), "rank"(Y))$

In order to select the most relevant tickers, the 3 correlation matrices have been computed once with the whole dataset. Then, only the 65% most correlated tickers were kept and only the common date range between all tickers were kept. Then the computation of the 3 correlation matrices were started again to have more accurate values.

The following tickers have more than 65% of correlation (with respect to Pierson's, Kendall's and Spearman's methods) with gold over the whole period and have been selected to be part of the time series:

#figure(
  table(
    columns: 4,
    stroke: none,
    align: (left + horizon),
    //inset: 3pt,
    table.hline(stroke: 0.5pt),                          table.vline(x: 0, start: 0, end: 15, stroke: 0.5pt), table.vline(x: 1, start: 0, end: 15, stroke: 0.5pt), table.vline(x: 2, start: 0, end: 15, stroke: 0.5pt),
    table.vline(x: 3, start: 0, end: 15, stroke: 0.5pt), table.vline(x: 4, start: 0, end: 15, stroke: 0.5pt), table.header(
      [*ticker*],
      [*Pierson*],
      [*Kendall*],
      [*Spearman*],
    ),
    table.hline(stroke: 0.5pt),                          [BTC],                                               [0.9107031967844699],                                [0.730110653102119],
    [0.9175005834238465],                                [GT],                                                [0.872068366942732],                                 [],
    [0.7556076533399873],                                [SOL],                                               [0.872068366942732],                                 [],
    [0.7116827915226329],                                [BNB],                                               [0.870625369815244],                                 [],
    [0.6897266806989514],                                [TRX],                                               [0.865148992461277],                                 [0.7023226930482401],
    [0.8838661408310834],                                [SUN],                                               [0.831424628414087],                                 [],
    [0.7411085422153962],                                [ETH],                                               [0.7737201985896954],                                [0.6539055159233185],
    [0.8732200136775444],                                [RAY],                                               [0.7691850017394904],                                [],
    [],                                                  [FET],                                               [0.7599349834769431],                                [0.7124420078786323],
    [0.9065053525645362],                                [APE],                                               [-0.6945792605468512],                               [],
    [-0.7850699740155144],                               [LEO],                                               [0.6721238538115092],                                [],
    [],                                                  [DOGE],                                              [],                                                  [],
    [0.7364563538003932],                                [XRP],                                               [],                                                  [],
    [0.6927795287025804],                                [LINK],                                              [],                                                  [],
    [0.6619425674230894],                                table.hline(stroke: 0.5pt),
  ),
  caption: "Tickers correlation with gold",
)

#figure(
  image("/resources/img/corrmat_pearson.png", width: 14cm),
  caption: "Correlation matrix with respect to the Pearson computation",
)
#figure(
  image("/resources/img/corrmat_kendall.png", width: 14cm),
  caption: "Correlation matrix with respect to the Kendall computation",
)
#figure(
  image("/resources/img/corrmat_spearman.png", width: 14cm),
  caption: "Correlation matrix with respect to the Spearman computation",
)

== Time series

=== Algorithms
With the most correlated cryptocurrencies writen as exogenous datas in the time series of gold price, we tried to predict gold price using three algorithms:
+ Naive model
+ ARIMA/SARIMA model
+ Deep learning model (LSTM)
+ a combination of the last two

ARIMA/SARIMA seams to have the best results with only time based data. So we choosed to train it beside Long Short Term Memory (LSTM).

=== Implementation

- Naive model: This is chosen as a baseline, the logic here is tomorrow's price = today's price. Because gold prices fluctuate very little in the short term, we think this is a good benchmark.
- ARIMA: Because gold prices tend to revert to the mean in the long run, prices fluctuate over time, and past prices influence future prices. ARIMA can capture the linear trend and autocorrelation of gold price changes.
- SARIMA: SARIMA and ARIMA operate on similar principles, but SARIMA incorporates seasonal patterns. Because gold prices are linked to seasonal demand (e.g., as holiday gifts or wedding jewelry) and cultural patterns (e.g., the Indian wedding season and Chinese New Year), we believe economic cycles may exist. Additionally, the seasons in mining areas also affect production, thus influencing prices.
- Deep learning: Long Short Term Memory is a CNN that can control the information stream, and so to keep important data over long sequences of dates.
*/
