import PyInstaller.__main__
import os
import customtkinter

# CustomTkinterの場所を特定
ctk_path = os.path.dirname(customtkinter.__file__)

import nudenet
nudenet_path = os.path.dirname(nudenet.__file__)

PyInstaller.__main__.run([
    'main.py',
    '--name=AutoBlur-NN',
    '--noconsole',
    '--onedir',
    f'--add-data={ctk_path};customtkinter/',
    f'--add-data={nudenet_path};nudenet/', # NudeNetのONNXモデルを含める
    '--add-data=App;App',
    '--hidden-import=tkinter',
    '--hidden-import=tkinter.filedialog',
    '--hidden-import=tkinter.messagebox',
    '--hidden-import=tkinter.font',
    '--hidden-import=tkinter.ttk',
    '--hidden-import=darkdetect',
    '--hidden-import=nudenet',
    '--hidden-import=onnxruntime',
    '--hidden-import=cv2',
    '--clean',
    '--noconfirm',
])
