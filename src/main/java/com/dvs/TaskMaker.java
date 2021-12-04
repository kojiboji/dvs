package com.dvs;

import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.List;

import static java.lang.Math.min;

public class TaskMaker {
    private final String name;
    private final int taskDuration;
    private final ArrayList<ArrayList<Segment> > segmentLists;
    public List<Task> tasks;

    public TaskMaker(String name, int taskDuration, ArrayList<ArrayList<Segment>> segmentLists){
        this.name = name;
        this.taskDuration = taskDuration;
        this.segmentLists = segmentLists;
        this.tasks = createTasks();
    }

    private @NotNull List<Task> createTasks(){
        double minDuration = Double.MAX_VALUE;
        for (ArrayList<Segment> singleVideoSegment: segmentLists) {
            double videoDuration = singleVideoSegment.get(singleVideoSegment.size() - 1).getEndTime();
            minDuration = min(videoDuration, minDuration);
        }
        List<Task> tasks = new ArrayList<>();
        for(double start = 0; start < minDuration; start+=taskDuration) {
            tasks.add(new Task(name, start, min(start+taskDuration, minDuration), segmentLists.size()));
        }
        int[] listIndices = new int[segmentLists.size()];
        for(Task task: tasks){
            for(int listIndex = 0; listIndex < listIndices.length; listIndex++){
                if( listIndices[listIndex] > 0) {
                    listIndices[listIndex]--;
                }
                while(listIndices[listIndex] < segmentLists.get(listIndex).size()) {
                    Segment nextSegment = segmentLists.get(listIndex).get(listIndices[listIndex]);
                    if (nextSegment.overlaps(task)) {
                        task.addSegment(listIndex, nextSegment);
                        listIndices[listIndex]++;
                    } else {
                        break;
                    }
                }
            }
        }
        return tasks;
    }

    public List<Task> getTasks() {
        return tasks;
    }
}
