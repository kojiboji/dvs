package com.dvs;

import java.io.Serializable;
import java.util.ArrayList;

public class Task implements Serializable {
    private String basename;
    private double start;
    private double end;
    private ArrayList<ArrayList<Segment>> segments;

    public Task(){};

    public Task(String basename, double start, double end, int size) {
        this.basename = String.format("%s-%f-%f%s", basename, start, end, Config.VID_EXT);
        this.start = start;
        this.end = end;
        segments = new ArrayList<>(size);
        for(int i = 0; i < size; i++){
            segments.add(new ArrayList<Segment>());
        }
    }

    public double getStart() {
        return start;
    }

    public double getEnd() {
        return end;
    }

    public String getBasename() {
        return basename;
    }

    public String getLocalName() {
        return Config.DIR_STITCH + basename;
    }

    public ArrayList<ArrayList<Segment>> getSegments() {
        return segments;
    }

    public void setBasename(String basename) {
        this.basename = basename;
    }

    public void setStart(double start) {
        this.start = start;
    }

    public void setEnd(double end) {
        this.end = end;
    }

    public void setSegments(ArrayList<ArrayList<Segment>> segments) {
        this.segments = segments;
    }

    public void addSegment(int index, Segment segment){
        this.segments.get(index).add(segment);
    }

    public String toString(){
        return String.format("%f:%f\n%s\n", start, end, segments);
    }
}
