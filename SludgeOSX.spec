# -*- mode: python -*-
a = Analysis(['/Users/Shellane/DPS_PIPELINE/Sludge.py'],
             pathex=['\\'],
             hiddenimports=[],
             hookspath=['/Users/Shellane/DPS_PIPELINE/.'],
             runtime_hooks=None)
a.datas += [('ui/xganttwidget.ui', '/Users/Shellane/DPS_PIPELINE/projexui/widgets/xganttwidget/ui/xganttwidget.ui', 'DATA')]
a.datas += [('ui/createprojectwidget.ui', '/Users/Shellane/DPS_PIPELINE/DPSPipeline/widgets/createprojectwidget/ui/createprojectwidget.ui', 'DATA')]
a.datas += [('ui/projectviewwidget.ui', '/Users/Shellane/DPS_PIPELINE/DPSPipeline/widgets/projectviewwidget/ui/projectviewwidget.ui', 'DATA')]
a.datas += [('ui/seqDescription.ui', '/Users/Shellane/DPS_PIPELINE/DPSPipeline/widgets/projectviewwidget/ui/seqDescription.ui', 'DATA')]
a.datas += [('ui/hourswidget.ui', '/Users/Shellane/DPS_PIPELINE/DPSPipeline/widgets/hourswidget/ui/hourswidget.ui', 'DATA')]
a.datas += [('ui/mytaskswidgetitem.ui', '/Users/Shellane/DPS_PIPELINE/DPSPipeline/widgets/mytaskswidgetitem/ui/mytaskswidgetitem.ui', 'DATA')]
a.datas += [('ui/AEshot.ui', '/Users/Shellane/DPS_PIPELINE/DPSPipeline/widgets/attributeeditorwidget/ui/AEshot.ui', 'DATA')]
a.datas += [('ui/AEProject.ui', '/Users/Shellane/DPS_PIPELINE/DPSPipeline/widgets/attributeeditorwidget/ui/AEProject.ui', 'DATA')]
a.datas += [('ui/loginwidget.ui', 'DPSPipeline/widgets/loginwidget/ui/loginwidget.ui', 'DATA')]
a.datas += [('projexui/resources/default/img/treeview/triangle_down.png', '/Users/Shellane/DPS_PIPELINE/projexui/resources/default/img/treeview/triangle_down.png', 'DATA')]
a.datas += [('projexui/resources/default/img/treeview/triangle_right.png', '/Users/Shellane/DPS_PIPELINE/projexui/resources/default/img/treeview/triangle_right.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/folder.png', '/Users/Shellane/DPS_PIPELINE/projexui/resources/default/img/DP/folder.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/noImage.png', '/Users/Shellane/DPS_PIPELINE/projexui/resources/default/img/DP/noImage.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/Statuses/notStarted.png', '/Users/Shellane/DPS_PIPELINE/projexui/resources/default/img/DP/Statuses/notStarted.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/Statuses/inProgress.png', '/Users/Shellane/DPS_PIPELINE/projexui/resources/default/img/DP/Statuses/inProgress.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/Statuses/needsAttention.png', '/Users/Shellane/DPS_PIPELINE/projexui/resources/default/img/DP/Statuses/needsAttention.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/Statuses/readyForApproval.png', '/Users/Shellane/DPS_PIPELINE/projexui/resources/default/img/DP/Statuses/readyForApproval.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/Statuses/done.png', '/Users/Shellane/DPS_PIPELINE/projexui/resources/default/img/DP/Statuses/done.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/Statuses/none.png', '/Users/Shellane/DPS_PIPELINE/projexui/resources/default/img/DP/Statuses/none.png', 'DATA')]
a.datas += [('projexui/resources/default/img/DP/pipe.gif', 'projexui/resources/default/img/DP/pipe.gif', 'DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Sludge',
          debug=False,
          strip=None,
          upx=True,
          console=False,
		  icon = 'pipe.icns')

app = BUNDLE(exe,
			 name = 'Sludge.app',
			 icon = 'pipe.icns')
