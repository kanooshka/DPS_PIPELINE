# -*- mode: python -*-
a = Analysis(['application.py'],
             pathex=['\\'],
             hiddenimports=[],
             hookspath=['.'],
             runtime_hooks=None)
a.datas += [('ui/xganttwidget.ui', 'projexui/widgets/xganttwidget/ui/xganttwidget.ui', 'DATA')]
a.datas += [('ui/createprojectwidget.ui', 'DPSPipeline/widgets/createprojectwidget/ui/createprojectwidget.ui', 'DATA')]
a.datas += [('projexui/resources/default/img/treeview/triangle_down.png', 'projexui/resources/default/img/treeview/triangle_down.png', 'DATA')]
a.datas += [('projexui/resources/default/img/treeview/triangle_right.png', 'projexui/resources/default/img/treeview/triangle_right.png', 'DATA')]
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
          console=True )
