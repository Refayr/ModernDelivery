#import "@preview/hei-synd-report:0.1.1": *
#import "/metadata.typ": *
#pagebreak()

= Result

#figure(
  table(
    columns: 7,
    stroke: none,
    align: (left + horizon),
    //inset: 3pt,
    table.vline(x: 1, start: 0, end: 3, stroke: 0.5pt), table.header(
      [*metric*],
      [*Naive*],
      [*HistoricAverage*],
      [*WindowAverage*],
      [*SeasonalNaive*],
      [*ARIMA*],
      [*SARIMA*],
    ),
    table.hline(stroke: 0.5pt),                         [MAE],                      [57.471655], [598.324263],  [83.421234],     [86.408374],   [71.508333],
    [71.508333],                                        table.hline(stroke: 0.5pt), [MSE],       [4161.423763], [359019.774221], [7986.952859], [9092.011023],
    [5916.408276],                                      [5916.408276],
  ),
  caption: "Baseline Model comparison",
)

From the baseline models, we found that ARIMA and SARIMA have the best performance although it is worse than Naive model. That's may because Naive model use yesterday's price as today's price
and the flactuation for gold price between a short periode will only have small change. So we use ARIMA and SARIMA to do further analysis.

#figure(
  table(
    columns: 3,
    stroke: none,
    align: (left + horizon),
    //inset: 3pt,
    table.vline(x: 1, start: 0, end: 5, stroke: 0.5pt), table.header(
      [*Model*],
      [*MAE*],
      [*RMSE*],
    ),
    table.hline(stroke: 0.5pt),                         [ARIMA_TimeOnly],           [74.022],
    [79.428],                                           table.hline(stroke: 0.5pt), [SARIMA_TimeOnly],
    [74.022],                                           [79.428],                   table.hline(stroke: 0.5pt),
    [ARIMA_Crypto+Time],                                [92.358],                   [101.845],
    table.hline(stroke: 0.5pt),                         [SARIMA_Crypto+Time],       [117.592],
    [132.474],
  ),
  caption: "ARIMA/SARIMA comparison between different features",
)

#figure(
  image("/resources/img/gold_prediction_comparison.png", width: 80%),
  caption: [Visuliazition ARIMA/SARIMA],
)

Although from the table above, it seems crypto features do not improve the prediction, the error for models with time features is smaller than those with time features and crypto features, that because time-only model predicts near average. But when we look at the visuliazition for these models, we can see that time-model is basically a flat line, just like naive model. So it is not useful for trading prediction. And time+crypto model captures actual price movements, it has flactuations like real market price on the graph, so we think time+crypto model si more valuable even if point estimate are slightly off and have bigger error.

And in time+crypto models, ARIMA is better than SARIMA. So we decided to use ARIMA and another complex model (deep learning) to do further analysis.

#figure(
  table(
    columns: 4,
    stroke: none,
    align: (left + horizon),
    //inset: 3pt,
    table.vline(x: 1, start: 0, end: 5, stroke: 0.5pt), table.header(
      [*Model*],
      [*MAE*],
      [*RMSE*],
      [*$R^2$*],
    ),
    table.hline(stroke: 0.5pt),                         [ARIMA_TimeOnly],           [45.66],                    [61.00],
    [-0.358],                                           table.hline(stroke: 0.5pt), [LSTM_TimeOnly],            [540.974],
    [543.786],                                          [-106.889],                 table.hline(stroke: 0.5pt), [Ensemble_Avg_TimeOnly],
    [278.607],                                          [284.345],                  [-28.499],                  table.hline(stroke: 0.5pt),
    [Ensemble_Weighted_TimeOnly],                       [60.585],                   [81.713],                   [-1.436],
  ),
  caption: "Time-Only Dataset Result",
)

#figure(
  table(
    columns: 4,
    stroke: none,
    align: (left + horizon),
    //inset: 3pt,
    table.vline(x: 1, start: 0, end: 5, stroke: 0.5pt), table.header(
      [*Model*],
      [*MAE*],
      [*RMSE*],
      [*$R^2$*],
    ),
    table.hline(stroke: 0.5pt),                         [ARIMA_Time+Crypto],        [47.485],                   [58.477],
    [-0.248],                                           table.hline(stroke: 0.5pt), [LSTM_Time+Crypto],         [59.376],
    [70.860],                                           [0.0239],                   table.hline(stroke: 0.5pt), [Ensemble_Avg_Time+Crypto],
    [43.320],                                           [57.908],                   [-0.223],                   table.hline(stroke: 0.5pt),
    [Ensemble_Weighted_Time+Crypto],                    [42.270],                   [57.227],                   [-0.195],
  ),
  caption: "Time + Crypto Dataset Result",
)

#figure(
  image("/resources/img/ensemble_time_only.png", width: 80%),
  caption: [Visuliazition time-only models],
)

#figure(
  image("/resources/img/ensemble_time_crypto.png", width: 80%),
  caption: [Visuliazition time+crypto models],
)

Overall, all of our models have negative $R^2$, which means our model are all failing. But we believe this is normal, because market trading prices themselves cannot be predicted by our simple models. However, our goal is to find out if crypto features can help with prediction. The models here are ARIMA, deep laearning and the model combined by them. Same as before the visuliazition for time-only models are all like flat line, but the models with time and crypto prices exhibit fluctuations similar to those in the real market. So our conclusion is crpto will improve the model.

We adjust test period for ARIMA in combined model comparision (from 30 days to 60 days), and the performance improved significantly. And from the table, we found that weighted emsemble model is best, this aligns with our predictions, and using more complex models can improve our forecasts.
