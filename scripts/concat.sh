# $1 is a file that has the name of all the video files to concat
# $2 output name from dvs.sh
tmp_dir=/tmp/concat/
mkdir -p ${tmp_dir}
# download all panorama segments from s3
xargs -n 1 -P 0 -I % sh -c "aws s3api get-object --bucket dvs-stitch --key % ${tmp_dir}% >/dev/null" < "$1"
# create a file that can be read by ffmpeg concat
sed -e 's/^/file /' "$1"  > "${tmp_dir}${2}.txt"
ffmpeg -f concat -i "${tmp_dir}${2}.txt" -c copy ${2}.mp4 -y