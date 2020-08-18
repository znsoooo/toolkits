一键安装放置在同级目录文件夹内的python库文件。

一键安装脚本放置在多个文件夹的同级目录下，通过文件夹命名控制python库的安装顺序。文件夹内放置python库的安装包，格式支持gz、zip和whl（需先安装pip）。



我目前应用的案例的目录结构：





~/一键安装.py



~/1_pip和setuptools\pip-18.1.tar.gz

~/1_pip和setuptools\setuptools-40.6.3.zip



~/2_pyinstaller_step1\altgraph-0.16.1.tar.gz

~/2_pyinstaller_step1\future-0.17.1.tar.gz

~/2_pyinstaller_step1\macholib-1.11.tar.gz

~/2_pyinstaller_step1\pefile-2018.8.8.tar.gz

~/2_pyinstaller_step1\pywin32-ctypes-0.2.0.tar.gz



~/2_pyinstaller_step2\PyInstaller-3.4.tar.gz



~/3_main_step1\colorama-0.4.1.tar.gz

~/3_main_step1\numpy-1.15.4-cp36-none-win_amd64.whl

~/3_main_step1\Pillow-5.3.0-cp36-cp36m-win_amd64.whl

~/3_main_step1\Pypubsub-4.0.0.zip

~/3_main_step1\pyserial-3.4.tar.gz

~/3_main_step1\pywin32-224-cp36-cp36m-win_amd64.whl

~/3_main_step1\six-1.12.0.tar.gz



~/3_main_step2\opencv_python-3.1.0.5-cp36-cp36m-win_amd64.whl

~/3_main_step2\qrcode-5.3.tar.gz

~/3_main_step2\vtk-8.1.2-cp36-cp36m-win_amd64.whl

~/3_main_step2\wxPython-4.0.3-cp36-cp36m-win_amd64.whl

