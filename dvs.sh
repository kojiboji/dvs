# 1 is output name
# 2 is file segment size
# rest are input videos

videos=("${@:3}")

#segment videos
for vid in "${videos[@]}"
do
  scripts/segment.sh "$vid" "$2"
done

csvs=()
for vid in "${videos[@]}"
do
  filename="$(basename -- $vid)"
  filename="${filename%.*}"
  filename="/tmp/segment/${filename}.csv"
  csvs+=("$filename")
done

mkdir -p /tmp/concat/

#stitch videos
spark-submit --class com.dvs.App app/build/libs/app-all.jar "$1" "$2" "${csvs[@]}" > "/tmp/concat/${1}_base.txt"

#concat videos
scripts/concat.sh "/tmp/concat/${1}_base.txt" "$1"