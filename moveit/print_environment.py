"""Emit only activation-related variables for the PowerShell/CMD bridge."""
import json
import os
names = {'PATH', 'PYTHONPATH', 'PYTHONHOME', 'CMAKE_PREFIX_PATH', 'PKG_CONFIG_PATH',
         'SSL_CERT_FILE', 'SSL_CERT_DIR', 'OPENSSL_CONF', 'OPENSSL_MODULES',
         'PROJ_DATA', 'PROJ_LIB', 'GDAL_DATA'}
prefixes = ('CONDA_', 'PIXI_', 'ROS_', 'AMENT_', 'COLCON_', 'RMW_', 'QT_', 'QML', 'GZ_', 'SDF_')
print(json.dumps({k: v for k, v in os.environ.items() if k in names or k.startswith(prefixes)}))
