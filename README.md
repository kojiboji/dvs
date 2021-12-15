# Distributed Video Stitching
## Introduction
Master's project to stitch overlapping videos into a panorama. Since the operation is computationally expensive, this project uses Spark to coordinate execution across multiple nodes.

## Files

* __README.md__: This file, contains information on project files and how to setup/run the program on a cluster
* __/dvs__: A directory containing Python files that are executed by the cluster
  * __app.py__: A python program that stitches a list of overlapping video segments into segments of panorama video
  * __constants.py__: Contains different constants such as the names of tmp directories and S3 buckets
  * __task.py__: Creates tasks for Spark executors
  * __stitch.py__: Executes tasks by stitching together the tasks' assigned segments
* __/scripts__: A directory containing a variety of scripts
  * __clean.sh__: Removes temporary files on the driver and in S3
  * __concat.sh__: Concatenates a list of video segments into a single video (used by dvs.sh)
  * __duplicate.sh__: Duplicates videos for parallelizing tests on the same video
  * __segment.sh__: Splits a video (on keyframes) into segments of a specified length (used by dvs.sh)
  * __setup.sh__: Installs necessary software on a AWS Linux 2 EC2 instance
  * __zip_py.sh__: zips python files so that they can be sent to Spark executors (used by dvs.sh)
* __dvs.sh__: Stitches together overlapping videos
* __pyfiles.zip__: The zipped python files used by a Spark executor
* __requirements.txt__: Generated from "pip freeze"
* __video_files.txt__: A list of videos used for testing (useful for input to xargs)

## Running the Project
0. spin up a AWS Linux 2 EC2 instance
   1. make sure that you can access the instance from port 22 (ssh) and 8080 (spark master gui)
   2. if running in cluster, make sure that all intances in the same security group can talk to each other
1. copy the setup.sh file onto the machine using ssh
    > scp -i <pem file> <path to /scripts>/setup.sh ec2-user@<instance dns name>:~
   
    > scp -i ~/dev/aws/dvs/dvs.pem scripts/setup.sh ec2-user@ec2-13-56-77-2.us-west-1.compute.amazonaws.com:~
2. ssh into the machine and run the setup file
    > ./setup.sh
3. setup s3 buckets
   1. create two s3 buckets, one for segments before they are stitched (PRE), and one for segments after they are stitched (STITCH)
   2. modify constants.py so that BUCKET_PRE and BUCKET_STITCH are set to the names of s3 buckets
   3. configure the ec2 instance so that it can access to bucket
      1. create a role that can read and write to s3
      2. run aws-configure
4. download the videos to the instance
### Locally
5. set the SPARK_MASTER variable so that spark runs locally
    > export SPARK_MASTER=local[*]
6. run the ./dvs.sh command
    > ./dvs.sh <output-name> <segment-size> <min_overlap> <left_video> <right_video>
   
    > ./dvs.sh out 10 0.5 videos/juggle_l_240.mp4 videos/juggle_r__240.mp4

    * segment-size should be significant larger that the average time between key-frames
      * 10 seconds seems to be a good default
    * min_overlap should be the minimum amount of each frame that overlaps
      * if min_overlap is 1 that means the views overlap entirely
      * if min_overlap is 0 then the views do not overlap at all
      * if min_overlap is 0.5 then one half of each view overlaps with the other view

### In a cluster
5. spin up as many other instances as desired
   * make sure to run the setup script on worker instances
   * make sure to run aws-configure as well
6. start a master on one node
    > start-master
7. using a browser connect to the master on port 8080
8. copy the spark master url
9. startup a worker on every node
    > start-worker <spark-master-url> 
   
    > start-worker spark://ip-172-31-1-6.us-west-1.compute.internal:7077
10. On the master node, set the SPARK_MASTER
    > export SPARK_MASTER=<spark-master-url>

    > export SPARK_MASTER=spark://ip-172-31-1-6.us-west-1.compute.internal:7077
11. run the ./dvs.sh command
    > ./dvs.sh <output-name> <segment-size> <min_overlap> <left_video> <right_video>
    
    > ./dvs.sh out 10 0.5 videos/juggle_l_240.mp4 videos/juggle_r__240.mp4


