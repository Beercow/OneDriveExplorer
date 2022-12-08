# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


OneDriveExplorer_a = Analysis(['OneDriveExplorer.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

OneDriveExplorer_pyz = PYZ(OneDriveExplorer_a.pure, OneDriveExplorer_a.zipped_data,
             cipher=block_cipher)

OneDriveExplorer_a.datas += [('ode\\helpers\\schema', './ode\\helpers\\schema', 'DATA')]

OneDriveExplorer_exe = EXE(OneDriveExplorer_pyz,
          OneDriveExplorer_a.scripts,
          OneDriveExplorer_a.binaries,
          OneDriveExplorer_a.zipfiles,
          OneDriveExplorer_a.datas,  
          [],
          name='OneDriveExplorer',
          icon='./Images/ode.ico',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

OneDriveExplorer_GUI_a = Analysis(['OneDriveExplorer_GUI.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

OneDriveExplorer_GUI_pyz = PYZ(OneDriveExplorer_GUI_a.pure, OneDriveExplorer_GUI_a.zipped_data,
             cipher=block_cipher)

OneDriveExplorer_GUI_splash = Splash('Images\\splashv.png',
                binaries=OneDriveExplorer_GUI_a.binaries,
                datas=OneDriveExplorer_GUI_a.datas,
                text_pos=(15, 260),
                text_size=12,
                text_color='#0364b8',
                minify_script=True)

OneDriveExplorer_GUI_a.datas += Tree('./Images', prefix='Images')
OneDriveExplorer_GUI_a.datas += [('ode\\helpers\\schema', './ode\\helpers\\schema', 'DATA')]

OneDriveExplorer_GUI_exe = EXE(OneDriveExplorer_GUI_pyz,
          OneDriveExplorer_GUI_a.scripts,
          OneDriveExplorer_GUI_a.binaries,
          OneDriveExplorer_GUI_a.zipfiles,
          OneDriveExplorer_GUI_a.datas,
          OneDriveExplorer_GUI_splash,
          OneDriveExplorer_GUI_splash.binaries,
          [],
          name='OneDriveExplorer_GUI',
          icon='./Images/ode.ico',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )