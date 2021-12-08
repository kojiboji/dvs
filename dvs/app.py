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
    parser.add_argument("min_overlap", help='the estimated minimum overlap between the videos, 0 corresponds to no '
                                            'overlap, 1 corresponds to videos that see the exact same scene, '
                                            'and 0.5 means that frames overlap in on half - the final pano would have '
                                            'a width 1.5x the width of an individual video', type=float)
    parser.add_argument('videos', metavar='V', nargs='+',
                        help='videos to stitch')
    args = parser.parse_args()

    s3_client = boto3.client('s3')

    segments_all = task.preprocess(args.videos, s3_client)

    tasks = task.make_tasks(args.name, args.slice_size, segments_all)

    spark = SparkSession.builder.appName("Dvs").getOrCreate()
    sc = spark.sparkContext
    data = sc.parallelize(tasks)

    processed = data.map(lambda t:
                         stitch.stitch(t, args.min_overlap)
                         ).collect()
    for file in processed:
        print(file)
