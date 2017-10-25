# -*- mode: python -*-
a = Analysis(['Sludge.py'],
             pathex=['\\'],
             hiddenimports=[],
             hookspath=['.'],
             runtime_hooks=None)
a.datas += [('ui/xganttwidget.ui', 'projexui/widgets/xganttwidget/ui/xganttwidget.ui', 'DATA')]
a.datas += [('ui/createprojectwidget.ui', 'DPSPipeline/widgets/createprojectwidget/ui/createprojectwidget.ui', 'DATA')]
a.datas += [('ui/loginwidget.ui', 'DPSPipeline/widgets/loginwidget/ui/loginwidget.ui', 'DATA')]
a.datas += [('ui/projectviewwidget.ui', 'DPSPipeline/widgets/projectviewwidget/ui/projectviewwidget.ui', 'DATA')]
a.datas += [('projexui/resources/default/img/treeview/triangle_down.png', 'projexui/resources/default/img/treeview/triangle_down.png', 'DATA')]
a.datas += [('projexui/resources/default/img/treeview/triangle_right.png', 'projexui/resources/default/img/treeview/triangle_right.png', 'DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Sludge.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='Sludge')
