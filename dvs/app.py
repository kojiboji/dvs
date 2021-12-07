import pprint
import argparse
import boto3
from pyspark.sql import SparkSession
import stitch
import task
import logging

# 0 is the job name ('out' creates an 'out.mp4')
# 1 is the size of each time slice
# rest of arguements are video file names
if __name__ == "__main__":
    logger = logging.getLogger("app")
    logger.info("Hello")

    parser = argparse.ArgumentParser(description='Stitch some videos into panoramas.')
    parser.add_argument("name", help='the job name ("out" creates an "out.mp4")')
    parser.add_argument("slice_size", help='the size to split the video in before distribution', type=int)
    parser.add_argument('videos', metavar='V', nargs='+',
                        help='videos to stitch')
    args = parser.parse_args()

    s3_client = boto3.client('s3')

    segments_all = task.preprocess(args.videos, s3_client)
    # pprint.pprint(segments_all)

    tasks = task.make_tasks(args.name, args.slice_size, segments_all)
    # pprint.pprint(tasks)

    spark = SparkSession.builder.appName("Dvs").getOrCreate()
    sc = spark.sparkContext
    data = sc.parallelize(tasks)

    processed = data.map(lambda p:
                         stitch.stitch(p)
                         ).collect()
    for file in processed:
        print(file)
