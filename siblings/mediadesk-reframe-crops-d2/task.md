# Reframe sources for social platforms without upscaling

`/root/work/sources.csv` lists source videos (`source_id, width, height` in pixels) and `/root/work/platforms.json` lists target platforms with `name`, `aspect` (`w:h`), `out_width` and `no_upscale`.

For every source and every platform (sources in file order, platforms in file order within each source) compute the largest centred crop with the platform's aspect: if the source is wider than the aspect, crop_h = H and crop_w = floor(H x aw / ah); otherwise crop_w = W and crop_h = floor(W x ah / aw). Round crop_w and crop_h down to even. crop_x = floor((W - crop_w) / 2) and crop_y = floor((H - crop_h) / 2), each rounded down to even. out_w is `out_width`, except that with `no_upscale` true and crop_w smaller than `out_width`, out_w = crop_w. out_h = out_w x ah / aw rounded to the nearest integer (halves up), then down to even.

Write `/root/work/crops.csv` with header `source_id,platform,crop_x,crop_y,crop_w,crop_h,out_w,out_h`, integers only.
