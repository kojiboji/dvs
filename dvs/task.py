import csv
import sys
import math
import constants
from typing import NamedTuple


class Task(NamedTuple):
    """A Task that canbe  processed by a Spark executor

    """
    name: str
    start_time: float
    end_time: float
    segments: list


class Segment(NamedTuple):
    """A video segment

    """
    file_name: str
    start_time: float
    end_time: float
    s3_url: str

    def overlaps(self, task):
        """Checks if a task and segment overlap

        :param task: Task
        :return: bool
        """
        # segment starts before task but overlaps
        # segment end after task but overlaps
        # segment is contained in task
        return ((self.start_time <= task.start_time <= self.end_time) or
                (self.start_time <= task.end_time <= self.end_time) or
                (task.start_time <= self.start_time and self.end_time <= task.end_time))


def preprocess(videos, s3_client):
    """Creates a list of segments read from the provided csvs

    :param videos: list of str
        the csv files produces by ffmpeg's segment
    :param s3_client: S3.Client
        a s3 client used to generate presigned urls
    :return: list of Segment
    """
    segments_all = []
    for csv_file in videos:
        segments_vid = []
        with open(csv_file, newline='') as opened_file:
            reader = csv.reader(opened_file)
            for row in reader:
                # create a presigned url so that we don't need to download new files and can directly access from s3
                response = s3_client.generate_presigned_url('get_object',
                                                            Params={'Bucket': constants.BUCKET_PRE,
                                                                    'Key': row[0]},
                                                            ExpiresIn=constants.EXPIRES_IN)
                segments_vid.append(Segment(row[0], float(row[1]), float(row[2]), response))
        segments_all.append(segments_vid)
    return segments_all


def make_tasks(name, slice_size, segments_all):
    """Creates Tasks and assigns appropriate Segments

    :param name: str
        the name of the output file
    :param slice_size:
        the size that tasks should be
    :param segments_all: list of list of Segment
        each sublist are the segments for one video
    :return: list of Task
    """
    shortest_vid_duration = sys.float_info.max
    for segments_vids in segments_all:
        shortest_vid_duration = min(shortest_vid_duration, segments_vids[-1].end_time)
    tasks = []
    for i in range(0, math.ceil(shortest_vid_duration), slice_size):
        end_time = min(i + slice_size, shortest_vid_duration)
        task_name = "%s-%f-%f%s" % (name, i, end_time, constants.VID_EXT)
        tasks.append(Task(task_name, float(i), end_time, [[] for _ in range(len(segments_all))]))
    next_video_ptr = [0] * len(segments_all)
    for task in tasks:
        for which_video in range(0, len(segments_all)):
            # backtrack once since segments overlap task boundaries
            if next_video_ptr[which_video] > 0:
                next_video_ptr[which_video] -= 1
            # if there are still segments that can be assigned
            while next_video_ptr[which_video] < len(segments_all[which_video]):
                next_segment = segments_all[which_video][next_video_ptr[which_video]]
                if next_segment.overlaps(task):
                    # add the new segment
                    task.segments[which_video].append(next_segment)
                    # advance to the next segment
                    next_video_ptr[which_video] += 1
                # no more overlaps
                else:
                    break
    return tasks
