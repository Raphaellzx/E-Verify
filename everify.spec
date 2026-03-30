
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/everify/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/everify/core/data/templates.json', 'src/everify/core/data'),
        ('web/templates', 'web/templates'),
        ('web/static', 'web/static')
    ],
    hiddenimports=[
        'everify.common.file',
        'everify.core.operations.operation_factory',
        'everify.core.operations.base_operation',
        'everify.core.services.entity_manager',
        'everify.core.services.template_manager',
        'everify.core.services.url_generator',
        'everify.core.services.verify_service',
        'everify.core.services.report_generator',
        'everify.core.utils.config',
        'everify.core.utils.logger',
        'everify.core.base.browser',
        'everify.core.base.document',
        'everify.core.base.image',
        'flask',
        'jinja2'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'tensorflow',
        'torch',
        'sklearn'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='everify',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
