1. Find `count_objects.py` (`find / -name count_objects.py`) and run `ls /root`.
2. Run `ffmpeg -i /root/super-mario.mp4 -vf "select='eq(pict_type,I)'" -vsync vfr /root/keyframes_%03d.png`, then `mogrify -colorspace Gray /root/keyframes_*.png` to convert in place.
3. For each sorted frame and each of `coin.png`, `enemy.png`, `turtle.png`, run `python3 count_objects.py --tool count --input_image F --object_image T --threshold 0.9 --dedup_min_dist 3` and parse the count.
4. Write `/root/counting_results.csv` with header `frame_id,coins,enemies,turtles` and frame_id as the full path `/root/keyframes_%03d.png`. Check it with `head` and `wc -l`.
