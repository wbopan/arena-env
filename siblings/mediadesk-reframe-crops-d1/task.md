# Reframe sources for social platforms

`/root/work/sources.csv` lists source videos (`source_id, width, height` in pixels) and `/root/work/platforms.json` lists target platforms with `name`, `aspect` (`w:h`) and `out_width`.

For every source and every platform (sources in file order, platforms in file order within each source) compute the largest centred crop with the platform's aspect: if the source is wider than the aspect, crop_h = H and crop_w = floor(H x aw / ah); otherwise crop_w = W and crop_h = floor(W x ah / aw). Then round crop_w and crop_h down to even numbers. crop_x = floor((W - crop_w) / 2) and crop_y = floor((H - crop_h) / 2), each also rounded down to even. The output size is out_w = `out_width` and out_h = out_w x ah / aw rounded to the nearest integer (halves up) and then down to even.

Write `/root/work/crops.csv` with header `source_id,platform,crop_x,crop_y,crop_w,crop_h,out_w,out_h`, integers only.
