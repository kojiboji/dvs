package com.dvs;

import com.opencsv.bean.CsvBindByPosition;

import java.io.Serializable;

public class Segment implements Serializable {
    @CsvBindByPosition(position = 0)
    private String basename;

    @CsvBindByPosition(position = 1)
    private double startTime;

    @CsvBindByPosition(position = 2)
    private double endTime;

    public Segment(){};

    public String getBasename() {
        return basename;
    }

    public String getLocalName() {
        return Config.DIR_PRE + basename;
    }

    public double getStartTime() {
        return startTime;
    }

    public double getEndTime() {
        return endTime;
    }

    public void setBasename(String basename) {
        this.basename = basename;
    }

    public void setStartTime(double startTime) {
        this.startTime = startTime;
    }

    public void setEndTime(double endTime) {
        this.endTime = endTime;
    }

    public boolean overlaps(double start, double end)  {
        return ((startTime <= start && start <= endTime) ||
                (startTime <= end && end <= endTime) ||
                (start <= startTime && endTime <= end));
    }
    public boolean overlaps(Task task)  {
       return  this.overlaps(task.getStart(), task.getEnd());
    }

    public String toString(){
        return String.format("%f:%f:%s", startTime, endTime, basename);
    }
}
