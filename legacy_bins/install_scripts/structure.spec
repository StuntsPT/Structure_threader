# -*- mode: python -*-

block_cipher = None


a = Analysis(['structure.py'],
             pathex=['.', './vars'],
             binaries=None,
             datas=None,
             hiddenimports=['vars.admixprop', 'vars.allelefreq', 'vars.utils', 'vars.marglikehood', 'scipy.special', 'scipy.optimize'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='fastStructure',
          debug=False,
          strip=False,
          upx=True,
          console=True )
