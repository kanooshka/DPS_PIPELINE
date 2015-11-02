# -*- mode: python -*-
a = Analysis(['application.py'],
             pathex=['\\'],
             hiddenimports=[],
             hookspath=['.'],
             runtime_hooks=None)
a.datas += [('ui/xganttwidget.ui', 'projexui/widgets/xganttwidget/ui/xganttwidget.ui', 'DATA')]
a.datas += [('ui/createprojectwidget.ui', 'DPSPipeline/widgets/createprojectwidget/ui/createprojectwidget.ui', 'DATA')]
a.datas += [('ui/loginwidget.ui', 'DPSPipeline/widgets/loginwidget/ui/loginwidget.ui', 'DATA')]
a.datas += [('ui/projectviewwidget.ui', 'DPSPipeline/widgets/projectviewwidget/ui/projectviewwidget.ui', 'DATA')]
a.datas += [('ui/seqDescription.ui', 'DPSPipeline/widgets/projectviewwidget/ui/seqDescription.ui', 'DATA')]
a.datas += [('ui/mytaskswidgetitem.ui', 'DPSPipeline/widgets/mytaskswidgetitem/ui/mytaskswidgetitem.ui', 'DATA')]
a.datas += [('ui/AEProject.ui', 'DPSPipeline/widgets/attributeeditorwidget/ui/AEProject.ui', 'DATA')]
a.datas += [('ui/AEshot.ui', 'DPSPipeline/widgets/attributeeditorwidget/ui/AEshot.ui', 'DATA')]
a.datas += [('projexui/resources/default/img/treeview/triangle_down.png', 'projexui/resources/default/img/treeview/triangle_down.png', 'DATA')]
a.datas += [('projexui/resources/default/img/treeview/triangle_right.png', 'projexui/resources/default/img/treeview/triangle_right.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/folder.png', 'projexui/resources/default/img/DP/folder.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/noImage.png', 'projexui/resources/default/img/DP/noImage.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/Statuses/notStarted.png', 'projexui/resources/default/img/DP/Statuses/notStarted.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/Statuses/inProgress.png', 'projexui/resources/default/img/DP/Statuses/inProgress.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/Statuses/needsAttention.png', 'projexui/resources/default/img/DP/Statuses/needsAttention.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/Statuses/done.png', 'projexui/resources/default/img/DP/Statuses/done.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/Statuses/none.png', 'projexui/resources/default/img/DP/Statuses/none.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/pipe.gif', 'projexui/resources/default/img/DP/pipe.gif', 'DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='application.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False,
		  icon = 'pipe.ico')
