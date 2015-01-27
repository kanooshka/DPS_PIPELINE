import DPSPipeline.ganttTest
reload(DPSPipeline.ganttTest)
reload


try:
    GTEST
except:
    GTEST = DPSPipeline.ganttTest.GanttTest()

GTEST._myXGanttWidget.activateWindow()
GTEST.AddProject()
GTEST.AddProject()
GTEST.AddProject()

GTEST._myXGanttWidget.show()
