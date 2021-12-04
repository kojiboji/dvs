rm -rf /tmp/segment
rm -rf /tmp/pre
rm -rf /tmp/stitch
rm -rf /tmp/concat

aws s3 rm s3://dvs-pre --recursive
aws s3 rm s3://dvs-stitch --recursive

rm out.mp4