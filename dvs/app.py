import argparse
import cv2
import numpy as np
import logging
import imutils
import math

# 0 is the job name ('out' creates an 'out.mp4')
# 1 min overlap
# rest of arguements are video file names


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


if __name__ == "__main__":
    logger = logging.getLogger("app")
    logger.info("Hello")

    parser = argparse.ArgumentParser(description='Stitch some videos into panoramas.')
    parser.add_argument("name", help='the job name ("out" creates an "out.mp4")')
    parser.add_argument("min_overlap", help='the estimated minimum overlap between the videos, 0 corresponds to no '
                                            'overlap, 1 corresponds to videos that see the exact same scene, '
                                            'and 0.5 means that frames overlap in on half - the final pano would have '
                                            'a width 1.5x the width of an individual video', type=float)
    parser.add_argument('videos', metavar='V', nargs='+',
                        help='videos to stitch')
    args = parser.parse_args()

    vid_caps = []
    for video_file in args.videos:
        vid_caps.append(cv2.VideoCapture(video_file, cv2.CAP_FFMPEG))

    vid_cap = vid_caps[0]
    fps = vid_cap.get(cv2.CAP_PROP_FPS)
    height = vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    n_vids = len(args.videos)
    height = even_up(math.ceil(height))
    width = even_up(math.ceil(width * (n_vids - (args.min_overlap * (n_vids - 1)))))
    video_shape = (height, width, 3)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter("%s.mp4" % args.name, fourcc, fps, (width, height))

    stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()

    okay = True
    n = 0
    while okay:
        n += 1
        if(n % (30) == 0):
            print(n/30, " seconds")
        frames = []
        ret = False
        for vid_cap in vid_caps:
            ret, frame = vid_cap.read()
            if not ret:
                break
            frames.append(frame)
        if not ret:
            break
        did_stitch, pano = stitcher.stitch(frames)
        if did_stitch == 0:
            to_write = simple_resize(pano, video_shape)
            video_writer.write(simple_resize(to_write, video_shape))


    video_writer.release()


