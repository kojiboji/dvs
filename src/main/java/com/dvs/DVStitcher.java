package com.dvs;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.GetObjectRequest;
import com.amazonaws.services.s3.model.PutObjectRequest;
import org.apache.log4j.Logger;
import org.bytedeco.opencv.opencv_core.Mat;
import org.bytedeco.opencv.opencv_core.MatVector;
import org.bytedeco.opencv.opencv_core.Size;
import org.bytedeco.opencv.opencv_stitching.Stitcher;
import org.bytedeco.opencv.opencv_videoio.VideoCapture;
import org.bytedeco.opencv.opencv_videoio.VideoWriter;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;

import static java.lang.Math.round;
import static org.bytedeco.opencv.global.opencv_imgproc.resize;
import static org.bytedeco.opencv.global.opencv_videoio.*;

public class DVStitcher {
    public Task task;
    private final Stitcher stitcher;
    private ArrayList<VideoCapture> videoCaptures;
    private ArrayList<Iterator<Segment>> segmentTracker;
    private VideoWriter videoWriter;
    private Size frameSize;
    private double fps;
    private final AmazonS3 s3Client;
    private static final Logger logger = Logger.getLogger(DVStitcher.class.getName());
    private static final int API_PREFERENCE = CAP_ANY;

    public DVStitcher(Task task) {
        this.task = task;
        stitcher = Stitcher.create();
        s3Client = AmazonS3ClientBuilder.standard()
                .withRegion(Config.REGION)
                .withCredentials(new ProfileCredentialsProvider())
                .build();
        prepFileSystem();
        initializeArrayLists();
        logger.info(String.format("Starting Task %f-%f", task.getStart(), task.getEnd()));
    }

    private void prepFileSystem(){
        File preDir = new File(Config.DIR_PRE);
        if (! preDir.exists()){
            preDir.mkdir();
        }
        File stitchDir = new File(Config.DIR_STITCH);
        if (! stitchDir.exists()){
            stitchDir.mkdir();
        }

        for(ArrayList<Segment> videoSegments: task.getSegments()){
            for(Segment segment: videoSegments){
                logger.info(String.format("Creating new file %s", segment.getLocalName()));
                File tmpFile = new File(segment.getLocalName());
                try {
                    if (tmpFile.createNewFile()) {
                        logger.info(String.format("Downloading file from s3 %s", segment.getBasename()));
                        s3Client.getObject(new GetObjectRequest(Config.BUCKET_PRE, segment.getBasename()), tmpFile);
                    }
                } catch (IOException e) {
                    logger.error(String.format("Failed to create tmp file for %s", segment.getLocalName()), e);
                }
            }
        }
    }

    private void initializeArrayLists() {
        videoCaptures = new ArrayList<>();
        segmentTracker = new ArrayList<>();
        for (ArrayList<Segment> videoSegments : task.getSegments()) {
            Iterator<Segment> segmentPointer = videoSegments.iterator();
            segmentTracker.add(segmentPointer);
            logger.info(String.format("Task %f-%f: segments %d", task.getStart(), task.getEnd(), videoSegments.size()));
            Segment firstSegment = segmentPointer.next();
            VideoCapture videoCapture = new VideoCapture(firstSegment.getLocalName(), API_PREFERENCE);
            double offset = (task.getStart() - firstSegment.getStartTime()) * 1000;
            logger.info(String.format("Task %f-%f: Camera @ %s: offset %f", task.getStart(), task.getEnd(), firstSegment.getBasename(), offset));
            boolean canSet = videoCapture.set(CAP_PROP_POS_MSEC, offset);
            logger.info(String.format("Task %f-%f: Camera @ %s: can set %s", task.getStart(), task.getEnd(), firstSegment.getBasename(), canSet));
            boolean isOpened = videoCapture.isOpened();
            logger.info(String.format("Task %f-%f: Camera @ %s: is %s open", task.getStart(), task.getEnd(), firstSegment.getBasename(), isOpened));
            videoCaptures.add(videoCapture);
        }
        fps = videoCaptures.get(0).get(CAP_PROP_FPS);
        logger.info(String.format("Task %f-%f: Camera fps %f", task.getStart(), task.getEnd(),fps));
    }

    public String stitch() {
        String localVideo = task.getLocalName();
        logger.info(String.format("Task %f-%f START", task.getStart(), task.getEnd()));
        Mat pano = new Mat();
        boolean cameraSetup = false;
        for(int i = 0; i < round((task.getEnd() - task.getStart()) * fps); i++){
            int statusCode = stitchFrame(pano, i);
            logger.info(String.format("Task %f-%f: Frame %d is %d", task.getStart(), task.getEnd(), i, statusCode));
            if(statusCode == 0){
                if(!cameraSetup){
                    frameSize = pano.size();
                    if(frameSize.width() % 2 != 0){
                        frameSize.width(frameSize.width() + 1);
                    }
                    if(frameSize.height() % 2 != 0){
                        frameSize.height(frameSize.height() + 1);
                    }
                    int fourcc = VideoWriter.fourcc((byte)'M', (byte)'J', (byte)'P', (byte)'G');
                    videoWriter = new VideoWriter(task.getLocalName(), fourcc, fps, frameSize);
                    cameraSetup = true;
                    logger.info(String.format("Task %f-%f: Opened video for writing @ %s", task.getStart(), task.getEnd(), localVideo));
                }
                else{
                    Mat placeHolder = new Mat();
                    resize(pano, placeHolder, frameSize);
                    pano = placeHolder;
                }
                logger.info(String.format("Task %f-%f:Frame %d", task.getStart(), task.getEnd(), i));
                videoWriter.write(pano);
            }
        }
        if(videoWriter != null && videoWriter.isOpened()) {
            videoWriter.close();
            logger.info(String.format("Task %f-%f: Closed video for writing @ %s", task.getStart(), task.getEnd(), localVideo));
            PutObjectRequest request = new PutObjectRequest(Config.BUCKET_STITCH, task.getBasename(), new File(localVideo));
            logger.info(String.format("Task %f-%f: Writing to s3", task.getStart(), task.getEnd()));
            s3Client.putObject(request);
            logger.info(String.format("Task %f-%f: END", task.getStart(), task.getEnd()));
            return task.getBasename();
        } else {
            logger.info(String.format("Task %f-%f: END EMPTY", task.getStart(), task.getEnd()));
            return null;
        }
    }

    private int stitchFrame(Mat pano, int n){
        MatVector images = new MatVector();
        for(int i = 0; i < videoCaptures.size(); i++) {
            Mat grabbed = new Mat();
            boolean frameRead = videoCaptures.get(i).read(grabbed);
            while(!frameRead){
                String nextVideo = segmentTracker.get(i).next().getLocalName();
                logger.info(String.format("\"Task %f-%f: Cycle to next video %s: frame %d\n", task.getStart(), task.getEnd(), nextVideo, n));
                videoCaptures.get(i).open(nextVideo, API_PREFERENCE);
                frameRead = videoCaptures.get(i).read(grabbed);
            }
            images.push_back(grabbed);
        }
        int statusCode = stitcher.estimateTransform(images);
        logger.info(String.format("\"Task %f-%f: frame %d: code %d\n", task.getStart(), task.getEnd(), n, statusCode));
        if(statusCode == 0) {
            return stitcher.composePanorama(images, pano);
        }
        else {
            return statusCode;
        }
    }
}

