xargs -I % sh -c "cp videos/% videos/a%" < video_files.txt
xargs -I % sh -c "cp videos/% videos/b%" < video_files.txt
xargs -I % sh -c "cp videos/% videos/c%" < video_files.txt