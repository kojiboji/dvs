import math
import constants
import cv2
import imutils
import numpy as np
import boto3
import os
import task


def stitch(t, min_overlap):
    os.makedirs(constants.DIR_STITCH, exist_ok=True)
    stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
    s3_client = boto3.client('s3')
    return stitch_task(t, stitcher, min_overlap, s3_client)


def stitch_task(t, stitcher, min_overlap, s3_client):
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
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                video_writer = cv2.VideoWriter(local_name, fourcc, fps, (width, height))
            to_write = simple_resize(pano, video_shape)
            did_write = True
            video_writer.write(simple_resize(to_write, video_shape))

    for vid_cap in video_captures:
        vid_cap.release()

    if video_writer is not None and did_write:
        video_writer.release()
        s3_client.upload_file(local_name, constants.BUCKET_STITCH, t.name)
        os.remove(local_name)
        return t.name
    else:
        return None


# write a numpy array 'a' into the h,w,d of the specified 'shape'
# so that we can write frames of different sizes to the same video
# if 'a' is larger than the specified shape, crop
# if 'a' is smaller, fill edges with black
def simple_resize(a, new_shape):
    if a.shape[0] == new_shape[0] and a.shape[1] == new_shape[1]:
        return a
    h = min(a.shape[0], new_shape[0])
    w = min(a.shape[1], new_shape[1])
    d = min(a.shape[2], new_shape[2])
    ret = np.zeros(new_shape, dtype=a.dtype)
    ret[0:h, 0:w, 0:d] = a[0:h, 0:w, 0:d]
    return ret


def even_up(n):
    return n if n % 2 == 0 else n + 1


def stitch_frame(video_captures, segment_trackers, stitcher):
    frames = []
    for i, vid_cap in enumerate(video_captures):
        can_grab = vid_cap.grab()
        while not can_grab:
            try:
                next_segment = next(segment_trackers[i])
                vid_cap.open(next_segment.s3_url)
                can_grab = vid_cap.grab()
            except StopIteration:
                return 2, None
    for vid_cap in video_captures:
        frames.append(vid_cap.retrieve()[1])
    return stitcher.stitch(frames)


def _initialize(t):
    video_captures = []
    segment_trackers = []
    for i, video_segments in enumerate(t.segments):
        segment_pointer = iter(video_segments)
        segment_trackers.append(segment_pointer)
        first_segment = next(segment_pointer)
        vid_cap = cv2.VideoCapture(first_segment.s3_url)
        offset = (t.start_time - first_segment.start_time) * 1000
        vid_cap.set(cv2.CAP_PROP_POS_MSEC, offset)
        video_captures.append(vid_cap)
    vid_cap = video_captures[0]
    fps = vid_cap.get(cv2.CAP_PROP_FPS)
    height = vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    return video_captures, segment_trackers, fps, height, width
