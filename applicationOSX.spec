# -*- mode: python -*-
a = Analysis(['/Users/Shellane/DPS_PIPELINE/application.py'],
             pathex=['\\'],
             hiddenimports=[],
             hookspath=['/Users/Shellane/DPS_PIPELINE/.'],
             runtime_hooks=None)
a.datas += [('ui/xganttwidget.ui', '/Users/Shellane/DPS_PIPELINE/projexui/widgets/xganttwidget/ui/xganttwidget.ui', 'DATA')]
a.datas += [('ui/createprojectwidget.ui', '/Users/Shellane/DPS_PIPELINE/DPSPipeline/widgets/createprojectwidget/ui/createprojectwidget.ui', 'DATA')]
a.datas += [('projexui/resources/default/img/treeview/triangle_down.png', '/Users/Shellane/DPS_PIPELINE/projexui/resources/default/img/treeview/triangle_down.png', 'DATA')]
a.datas += [('projexui/resources/default/img/treeview/triangle_right.png', '/Users/Shellane/DPS_PIPELINE/projexui/resources/default/img/treeview/triangle_right.png', 'DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='application',
          debug=False,
          strip=None,
          upx=True,
          console=True )