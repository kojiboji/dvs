import math
import constants
import cv2
import imutils
import numpy as np
import boto3
import os
import task


def stitch(t, min_overlap):
    """Stitches the segments specfied by the Task

    Parameters
    ----------
    :param t:
        the Task to be processed
    :param min_overlap: float
        the minimun overlap between views of the different cameras
    :return: str
        if successful, the s3 key of the generated panorama segment
        else, None
    """
    os.makedirs(constants.DIR_STITCH, exist_ok=True)
    stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
    s3_client = boto3.client('s3')
    return stitch_task(t, stitcher, min_overlap, s3_client)


def stitch_task(t, stitcher, min_overlap, s3_client):
    """Stitches after the necessary infrastructure has been setup
    Should not be called on its own

    :param t: Task
        the task to be processed
    :param stitcher: cv2.Stitcher
        a OpenCV stitcher
    :param min_overlap: float
        the minimun overlap between views of the different cameras
    :param s3_client: S3.Client
        the boto3 client used to upload/download videos
    :return:
        if successful, the s3 key of the generated panorama segment
        else, None
    """
    local_name = constants.DIR_STITCH + t.name
    video_captures, segment_trackers, fps, height, width = _initialize(t)
    video_writer = None
    did_write = False

    n_vids = len(t.segments)
    height = even_up(math.ceil(height))
    width = even_up(math.ceil(width * (n_vids - (min_overlap * (n_vids - 1)))))
    video_shape = (height, width, 3)

    for i in range(0, math.floor((t.end_time - t.start_time) * fps)):
        did_stitch, pano = stitch_frame(video_captures, segment_trackers, stitcher)
        if did_stitch == 0:
            if video_writer is None:
                #setup the output video
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                video_writer = cv2.VideoWriter(local_name, fourcc, fps, (width, height))
            to_write = simple_resize(pano, video_shape)
            did_write = True
            video_writer.write(to_write)

    for vid_cap in video_captures:
        vid_cap.release()

    if video_writer is not None and did_write:
        video_writer.release()
        s3_client.upload_file(local_name, constants.BUCKET_STITCH, t.name)
        os.remove(local_name)
        return t.name
    else:
        return None

def simple_resize(a, new_shape):
    """Resizes numpy array 'a' the h,w,d of the specified 'shape'

    :param a: ndarray
    :param new_shape: list of int
    :return: ndarray
    """
    if a.shape[0] == new_shape[0] and a.shape[1] == new_shape[1]:
        return a
    h = min(a.shape[0], new_shape[0])
    w = min(a.shape[1], new_shape[1])
    d = min(a.shape[2], new_shape[2])
    ret = np.zeros(new_shape, dtype=a.dtype)
    ret[0:h, 0:w, 0:d] = a[0:h, 0:w, 0:d]
    return ret


def even_up(n):
    """Takes a number and changes it to the next highest even number

    :param n: the base number
    :return: n rounded to the next highest even number
    """
    return n if n % 2 == 0 else n + 1


def stitch_frame(video_captures, segment_trackers, stitcher):
    """Stitches frames from open videos

    :param video_captures: list of cv2.VideoCapture
        the list of open videos to pull frames from
    :param segment_trackers: list of iterator of list of Segment
        list of iterators that point to next video segment
    :param stitcher: cv2.Stitcher
        the provided stitcher to do the actual stitching
    :return: int
        status code
    """
    frames = []
    for i, vid_cap in enumerate(video_captures):
        can_grab = vid_cap.grab()
        while not can_grab:
            try:
                next_segment = next(segment_trackers[i])
                vid_cap.open(next_segment.s3_url, cv2.CAP_FFMPEG)
                can_grab = vid_cap.grab()
            except StopIteration:
                # this can happen if we fail to open the video files
                return 2, None
    for vid_cap in video_captures:
        frames.append(vid_cap.retrieve()[1])
    return stitcher.stitch(frames)


def _initialize(t):
    """Setup videos

    :param t: Task
        the task to process
    :return: list of cv2.VideoCapture, list of iterator of list of Segment, double, double, double
    """
    video_captures = []
    segment_trackers = []
    for i, video_segments in enumerate(t.segments):
        segment_pointer = iter(video_segments)
        segment_trackers.append(segment_pointer)
        first_segment = next(segment_pointer)
        vid_cap = cv2.VideoCapture(first_segment.s3_url, cv2.CAP_FFMPEG)
        offset = (t.start_time - first_segment.start_time) * 1000
        vid_cap.set(cv2.CAP_PROP_POS_MSEC, offset)
        video_captures.append(vid_cap)
    vid_cap = video_captures[0]
    fps = vid_cap.get(cv2.CAP_PROP_FPS)
    height = vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    return video_captures, segment_trackers, fps, height, width
