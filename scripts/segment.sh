#$1 us video file
#$2 is step size

tmp_dir=/tmp/segment/

mkdir -p $tmp_dir

#find timestamps of each keyframe
key_frames=$(ffprobe \
  -hide_banner -loglevel error \
  -select_streams v \
  -show_frames \
  -skip_frame nokey \
  -show_entries 'frame=best_effort_timestamp_time' \
  -of csv \
  $1 |
cut -d ',' -f 2 |
grep -E '^[\.0-9]+$')
#put key_frames into and array
key_frames=($key_frames)

#find length video, round up to nearest integer
duration=$(ffprobe \
  -v error \
  -show_entries format=duration \
  -of csv \
  $1 |
cut -d ',' -f 2)
#divide by 1 so bc reads scale variable and rounds number
duration=$(echo "scale=0; ($duration + 0.5)/1" | bc)


#frames that "sandwich:" cuts, could have duplicates
dup_frames=()
i=0
for (( cut_time=$2 ; cut_time < duration ; cut_time+=$2)) ; do
  #find the two kfs that sandwich the cut
  frame_ahead=$(echo "$cut_time < ${key_frames[i]}" | bc)
  while [ "$frame_ahead" -ne 1 ] ; do
    #advance to next kf
    ((i+=1))
    #check if kf is ahead of cut
    frame_ahead=$(echo "$cut_time < ${key_frames[i]}" | bc)
    #if we cycled though all the kfs
    if [ "$i" -ge "${#key_frames[@]}" ] ; then
      break
    fi
  done

  #if we found a sandwich
  if [ "$frame_ahead" -eq 1 ] ; then
    if [ "$i" -ge 1 ] ; then
      dup_frames+=("${key_frames[$((i-1))]}")
    fi
    dup_frames+=("${key_frames[$i]}")
  #else, we cycled through all the kfs
  else
    dup_frames+=("${key_frames[$i]}")
    break
  fi
done

#remove duplicates
keep_frames=()
for f in "${dup_frames[@]}"; do
  if [ "${#keep_frames[@]}" -gt 0 ]; then
    if [ "$f" != "${keep_frames[${#keep_frames[@]} - 1]}" ] ; then
      if [ "${#keep_frames[@]}" -gt 1 ]; then
          if [ "$f" != "${keep_frames[${#keep_frames[@]} - 2]}" ] ; then
            keep_frames+=("$f")
          fi
      else
        keep_frames+=("$f")
      fi
    fi
    else
      echo what
      keep_frames+=("$f")
  fi
done

#do a pythonesque join with ,
echo "${keep_frames[@]}"
segment_times=""
for k in "${keep_frames[@]}" ; do
  segment_times="${segment_times},$k"
done
segment_times="${segment_times:1}"

filename="$(basename -- $1)"
filename="${filename%.*}"
ffmpeg -i "$1" -c copy -f segment -segment_list "${tmp_dir}${filename}.csv" -segment_list_type csv -segment_times "$segment_times" -reset_timestamps 1 "${tmp_dir}${filename}%03d.mp4"

#sed -i -e 's/^/\/tmp\//' "/tmp/${filename}.csv"
cut -f 1 -d ',' < "${tmp_dir}${filename}.csv" | xargs -I % sh -c "aws s3api put-object --bucket dvs-pre --key % --body ${tmp_dir}% >/dev/null"