# Weighted box search

The file `/root/work/lightcurve.csv` contains the columns `time_days,flux,reference,quality,sigma`. `flux` includes a slowly varying stellar signal; `reference` is the corresponding transit-free stellar model. A quality value of zero means usable photometry. `/root/work/trials.csv` contains candidate `period_days,duration_days` pairs.

Find the strongest box-shaped transit among the supplied trials. Keep only quality-zero rows, and use `flux/reference` as the normalized flux. Give each row weight `1/sigma²`. Let `tmin` be the earliest retained time. For each trial period P and each integer j from 0 through 39, test epoch `tmin + j*P/40`. A row is in transit when its circular distance from that epoch, modulo P, is at most half the trial duration. Compute the weighted mean normalized flux inside and outside transit. Depth is outside mean minus inside mean; score is depth divided by `sqrt(1/Winside + 1/Woutside)`, where W denotes summed weights. Select the combination with the greatest score; ties follow file order, then increasing j.

Write exactly one JSON object to `/root/work/box_result.json`, with numeric fields `period_days`, `epoch_days`, `depth_fraction`, and `snr`. Round them to 5, 5, 6, and 3 decimal places, respectively. Times and periods are in days; depth and snr are dimensionless.
