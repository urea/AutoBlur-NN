import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import webbrowser
from detector import SensitiveDetector
from processor import ImageProcessor
import cv2
import numpy as np

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Localization Dictionary
LANGUAGES = {
    "English": {
        "title": "AutoBlur-NN - AI Sensitive Content Blur Tool",
        "header": "AutoBlur-NN",
        "source_folder": "Source Folder:",
        "output_folder": "Output Folder:",
        "browse": "Browse",
        "threshold": "Sensitivity Threshold:",
        "area_scale": "Mosaic Area Scale (Tightness):",
        "process_method": "Process Method:",
        "exclude": "Exclude Categories (Skip):",
        "breast": "Breast",
        "genitalia": "Genitalia",
        "buttocks": "Buttocks",
        "start": "Start Processing",
        "log_err_folders": "[Error] Please specify both source and output folders.",
        "log_start": "[Info] Starting process in ",
        "log_no_files": "[Info] No image files found.",
        "log_found": "[Info] Found {0} images. Method: {1}, Scale: {2}",
        "log_warning_same": "[Warning] Source and Output folders are the same. This is a destructive process.",
        "log_skipped": "[Skipped] Could not read ",
        "log_detected": "[Detected] {0}: {1} regions found.",
        "log_failed_save": "[Error] Failed to save {0}. Is it open in another app?",
        "log_success": "[Success] Task finished.",
        "mosaic": "Mosaic",
        "blur": "Blur",
        "support": "Support this Project (note)"
    },
    "日本語": {
        "title": "AutoBlur-NN - AI自動ぼかしツール",
        "header": "AutoBlur-NN",
        "source_folder": "元フォルダ:",
        "output_folder": "出力先フォルダ:",
        "browse": "参照",
        "threshold": "検出感度 (低いほど厳格):",
        "area_scale": "モザイクの広さ (小さいほどタイト):",
        "process_method": "加工方法:",
        "exclude": "除外設定 (モザイクをかけない):",
        "breast": "胸部",
        "genitalia": "性器",
        "buttocks": "お尻",
        "start": "処理を開始する",
        "log_err_folders": "[エラー] 入力フォルダと出力フォルダを正しく指定してください。",
        "log_start": "[情報] 処理を開始します: ",
        "log_no_files": "[情報] 画像ファイルが見つかりませんでした。",
        "log_found": "[情報] {0}枚の画像が見つかりました。手法: {1}, 範囲係数: {2}",
        "log_warning_same": "[警告] 入力と出力が同じフォルダです。元の画像が上書きされます。",
        "log_skipped": "[スキップ] 読み込み失敗: ",
        "log_detected": "[検出] {0}: {1}箇所のセンシティブ領域が見つかりました。",
        "log_failed_save": "[エラー] {0} の保存に失敗しました。他のアプリで開いていませんか？",
        "log_success": "[完了] 全ての処理が終了しました。",
        "mosaic": "モザイク",
        "blur": "ぼかし",
        "support": "開発を支援する (note記事へ)"
    }
}

class AutoMosaicGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("800x650")

        # UI Variables
        self.lang = tk.StringVar(value="日本語")
        # 起動時は空にして、ユーザーに明示的に選択させる（安全のため）
        self.input_dir = tk.StringVar(value="")
        self.output_dir = tk.StringVar(value="")
        self.threshold = tk.DoubleVar(value=0.2)
        self.mosaic_scale = tk.DoubleVar(value=0.7)
        self.process_method = tk.StringVar(value="Mosaic")
        
        self.exclude_breast = tk.BooleanVar(value=True)
        self.exclude_genitalia = tk.BooleanVar(value=False)
        self.exclude_buttocks = tk.BooleanVar(value=True)

        self._create_widgets()
        self._update_language("日本語") # Initial Language

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        # Language Selector
        self.lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lang_frame.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="e")
        self.lang_btn = ctk.CTkSegmentedButton(self.lang_frame, values=["日本語", "English"], 
                                              variable=self.lang, command=self._update_language)
        self.lang_btn.pack()

        # Title Label
        self.title_label = ctk.CTkLabel(self, text="AutoMosaic", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=(10, 10))

        # Input Directory
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)
        self.lbl_source = ctk.CTkLabel(self.input_frame, text="Source Folder:", width=120, anchor="w")
        self.lbl_source.grid(row=0, column=0, padx=(10, 0), pady=10)
        ctk.CTkEntry(self.input_frame, textvariable=self.input_dir).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.btn_browse_in = ctk.CTkButton(self.input_frame, text="Browse", width=80, command=self._browse_input)
        self.btn_browse_in.grid(row=0, column=2, padx=10, pady=5)

        # Output Directory
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.output_frame.grid_columnconfigure(1, weight=1)
        self.lbl_output = ctk.CTkLabel(self.output_frame, text="Output Folder:", width=120, anchor="w")
        self.lbl_output.grid(row=0, column=0, padx=(10, 0), pady=10)
        ctk.CTkEntry(self.output_frame, textvariable=self.output_dir).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.btn_browse_out = ctk.CTkButton(self.output_frame, text="Browse", width=80, command=self._browse_output)
        self.btn_browse_out.grid(row=0, column=2, padx=10, pady=5)

        # Controls
        control_frame = ctk.CTkFrame(self)
        control_frame.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        control_frame.grid_columnconfigure((0, 1), weight=1)

        # Sliders
        sliders_subframe = ctk.CTkFrame(control_frame, fg_color="transparent")
        sliders_subframe.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.lbl_threshold = ctk.CTkLabel(sliders_subframe, text="Threshold:")
        self.lbl_threshold.pack(side="top", anchor="w")
        t_slider_frame = ctk.CTkFrame(sliders_subframe, fg_color="transparent")
        t_slider_frame.pack(fill="x")
        ctk.CTkSlider(t_slider_frame, from_=0.0, to=1.0, variable=self.threshold, command=self._on_threshold_change).pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.threshold_label = ctk.CTkLabel(t_slider_frame, text="0.20", width=40)
        self.threshold_label.pack(side="right")

        self.lbl_scale = ctk.CTkLabel(sliders_subframe, text="Scale:")
        self.lbl_scale.pack(side="top", anchor="w", pady=(5, 0))
        s_slider_frame = ctk.CTkFrame(sliders_subframe, fg_color="transparent")
        s_slider_frame.pack(fill="x")
        ctk.CTkSlider(s_slider_frame, from_=0.1, to=1.0, variable=self.mosaic_scale, command=self._on_scale_change).pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.scale_label = ctk.CTkLabel(s_slider_frame, text="0.70", width=40)
        self.scale_label.pack(side="right")

        # Excludes & Method
        exclude_subframe = ctk.CTkFrame(control_frame, fg_color="transparent")
        exclude_subframe.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.lbl_method = ctk.CTkLabel(exclude_subframe, text="Method:")
        self.lbl_method.pack(side="top", anchor="w")
        self.method_btn = ctk.CTkSegmentedButton(exclude_subframe, values=["Mosaic", "Blur"], variable=self.process_method)
        self.method_btn.pack(side="top", fill="x", pady=(0, 10))

        self.lbl_exclude = ctk.CTkLabel(exclude_subframe, text="Exclude:")
        self.lbl_exclude.pack(side="top", anchor="w")
        check_frame = ctk.CTkFrame(exclude_subframe, fg_color="transparent")
        check_frame.pack(side="top", fill="x")
        self.chk_breast = ctk.CTkCheckBox(check_frame, text="Breast", variable=self.exclude_breast)
        self.chk_breast.pack(side="left", padx=2)
        self.chk_genitalia = ctk.CTkCheckBox(check_frame, text="Genitalia", variable=self.exclude_genitalia)
        self.chk_genitalia.pack(side="left", padx=2)
        self.chk_buttocks = ctk.CTkCheckBox(check_frame, text="Buttocks", variable=self.exclude_buttocks)
        self.chk_buttocks.pack(side="left", padx=2)

        # Progress
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        self.start_btn = ctk.CTkButton(action_frame, text="Start", command=self._start_processing_thread)
        self.start_btn.pack(pady=5)
        self.progress_bar = ctk.CTkProgressBar(action_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0) # 初期値を0に設定

        # Log
        self.log_text = ctk.CTkTextbox(self)
        self.log_text.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.log_text.configure(state="disabled")

        # Support Button
        self.support_btn = ctk.CTkButton(self, text="Support", fg_color="transparent", border_width=1,
                                        command=self._open_support_link)
        self.support_btn.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")

    def _open_support_link(self):
        # ユーザー指定の正式なnote記事URL
        url = "https://note.com/limber_lynx1258/n/n1195d9e9de47"
        try:
            webbrowser.open(url)
        except Exception:
            # webbrowserが動作しない場合のフォールバック（Windows）
            if os.name == 'nt':
                os.startfile(url)

    def _update_language(self, lang_name):
        t = LANGUAGES[lang_name]
        self.title(t["title"])
        self.title_label.configure(text=t["header"])
        self.lbl_source.configure(text=t["source_folder"])
        self.lbl_output.configure(text=t["output_folder"])
        self.btn_browse_in.configure(text=t["browse"])
        self.btn_browse_out.configure(text=t["browse"])
        self.lbl_threshold.configure(text=t["threshold"])
        self.lbl_scale.configure(text=t["area_scale"])
        self.lbl_method.configure(text=t["process_method"])
        self.lbl_exclude.configure(text=t["exclude"])
        self.chk_breast.configure(text=t["breast"])
        self.chk_genitalia.configure(text=t["genitalia"])
        self.chk_buttocks.configure(text=t["buttocks"])
        self.start_btn.configure(text=t["start"])
        self.support_btn.configure(text=t["support"])
        
        # Update segmented button values and active state
        old_val = self.process_method.get()
        new_values = [t["mosaic"], t["blur"]]
        self.method_btn.configure(values=new_values)
        
        # Ensure the selection stays consistent during language toggle
        if old_val in ["Mosaic", "モザイク"]:
            self.process_method.set(t["mosaic"])
        else:
            self.process_method.set(t["blur"])

    def _on_threshold_change(self, value):
        self.threshold_label.configure(text=f"{value:.2f}")

    def _on_scale_change(self, value):
        self.scale_label.configure(text=f"{value:.2f}")

    def _browse_input(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            old_in = self.input_dir.get()
            old_out = self.output_dir.get()
            normalized_path = os.path.normpath(dir_path)
            self.input_dir.set(normalized_path)
            
            # 自動セット対象か判定（未設定、または「古いパス_output」「古いパス/output」の場合）
            if not old_out or old_out == os.path.normpath(old_in + "_output") or old_out == os.path.join(old_in, "output"):
                self.output_dir.set(os.path.normpath(normalized_path + "_output"))

    def _browse_output(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir.set(dir_path)

    def _log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _start_processing_thread(self):
        in_dir = self.input_dir.get()
        out_dir = self.output_dir.get()
        t = LANGUAGES[self.lang.get()]

        if not in_dir or not out_dir:
            self._log(t["log_err_folders"])
            return

        # 1. Drive Root Check (Safety)
        if os.path.dirname(in_dir) == in_dir or os.path.dirname(out_dir) == out_dir:
            self._log("[Error] Root directories (like C:\\) are restricted for safety.")
            tk.messagebox.showerror("Safety Error", "Processing a drive root directly is restricted for safety.\nPlease select a specific folder.")
            return

        # 2. Same Folder Check (Warning)
        if os.path.normpath(in_dir) == os.path.normpath(out_dir):
            ans = tk.messagebox.askyesno("Warning: Same Folder", 
                "Source and Output folders are the same.\n"
                "Original images WILL BE OVERWRITTEN.\n\n"
                "Do you want to continue?")
            if not ans:
                return

        self.start_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self._log("-" * 40)
        self._log(t["log_start"] + in_dir)
        
        thread = threading.Thread(target=self._run_process, daemon=True)
        thread.start()

    def _run_process(self):
        t = LANGUAGES[self.lang.get()]
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        threshold = self.threshold.get()
        mosaic_scale = self.mosaic_scale.get()
        method_val = self.process_method.get()
        
        # Method mapping back to internal English tags
        method = "Mosaic" if (method_val == "Mosaic" or method_val == "モザイク") else "Blur"

        exclude_list = []
        if self.exclude_breast.get(): exclude_list.append("BREAST")
        if self.exclude_genitalia.get(): exclude_list.extend(["GENITALIA", "VAGINA", "PENIS"])
        if self.exclude_buttocks.get(): exclude_list.extend(["BUTTOCKS", "ANUS"])

        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            detector = SensitiveDetector(threshold=threshold, exclude_keywords=exclude_list)
            processor = ImageProcessor()

            valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
            image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(valid_extensions)]
            total_files = len(image_files)

            if total_files == 0:
                self._log(t["log_no_files"])
                self.after(0, lambda: self.start_btn.configure(state="normal"))
                return

            self._log(t["log_found"].format(total_files, method, f"{mosaic_scale:.2f}"))

            if input_dir == output_dir:
                self._log(t["log_warning_same"])

            for i, filename in enumerate(image_files):
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, filename)

                boxes = detector.detect(input_path)
                # Loading and processing (Unicode safe read)
                img = cv2.imdecode(np.fromfile(input_path, dtype=np.uint8), cv2.IMREAD_COLOR)
                if img is None:
                    self._log(t["log_skipped"] + filename)
                    continue

                if boxes:
                    self._log(t["log_detected"].format(filename, len(boxes)))
                    for box in boxes:
                        x, y, w, h = map(int, box)
                        if method == "Mosaic":
                            img = processor.apply_mosaic(img, x, y, w, h, scale=mosaic_scale)
                        else:
                            img = processor.apply_blur(img, x, y, w, h, scale=mosaic_scale)
                
                # Write and check success (Unicode safe write)
                ext = os.path.splitext(output_path)[1]
                result, nparray = cv2.imencode(ext, img)
                success = False
                if result:
                    with open(output_path, mode='w+b') as f:
                        nparray.tofile(f)
                        success = True

                if not success:
                    self._log(t["log_failed_save"].format(filename))

                progress = (i + 1) / total_files
                self.after(0, lambda p=progress: self.progress_bar.set(p))

            self._log(t["log_success"])
        except Exception as e:
            self._log(f"[Error] {str(e)}")
        finally:
            self.after(0, lambda: self.start_btn.configure(state="normal"))

if __name__ == "__main__":
    app = AutoMosaicGUI()
    app.mainloop()
