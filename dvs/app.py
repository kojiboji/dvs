import cv2
import stitch
import task
import math
from pyspark.sql import SparkSession

if __name__ == "__main__":
    MESSAGE_SIZE = 250000000
    spark = SparkSession \
        .builder \
        .config("spark.driver.memory", "15g") \
        .config("spark.driver.maxResultSize", "15g") \
        .appName("PythonSimpleStitch") \
        .getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("INFO")
    left_camera = cv2.VideoCapture("/tmp/videos/seoul_3_l.mp4")
    right_camera = cv2.VideoCapture("/tmp/videos/seoul_3_r.mp4")

    FRAME_COUNT = max(left_camera.get(cv2.CAP_PROP_FRAME_COUNT),
                      right_camera.get(cv2.CAP_PROP_FRAME_COUNT))
    FRAME_WIDTH = max(left_camera.get(cv2.CAP_PROP_FRAME_WIDTH),
                      right_camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    FRAME_HEIGHT = max(left_camera.get(cv2.CAP_PROP_FRAME_HEIGHT),
                       right_camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # the two is a magic number, idk why its needed to adjust the size correctly
    numSlices = math.ceil((FRAME_COUNT * FRAME_WIDTH * FRAME_HEIGHT * 3 * 2) / MESSAGE_SIZE)
    # the two is a magic number, idk why its needed to adjust the size correctly
    imgs = task.img_gen(left_camera, right_camera)

    data = sc.parallelize(imgs, numSlices=2)
    processed = data.mapPartitions(lambda p: stitch.stitch(p)).collect()

    # height, width, depth
    shape = (0, 0, 0)
    for (status, img) in processed:
        if status == 0:
            shape = tuple([max(current, new) for current, new in zip(shape, img.shape)])
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter("/tmp/out.mp4", fourcc, 24.0, (shape[1], shape[0]))
    for (status, img) in processed:
        if status == 0:
            # cv2.imshow("image", zero_resize(img, shape))
            writer.write(stitch.zero_resize(img, shape))
            # cv2.waitKey(1)
    writer.release()