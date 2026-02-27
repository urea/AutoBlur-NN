# AutoMosaic 実装計画書 (配布・GUI対応版)

画像が含まれるフォルダを指定し、AIを用いてセンシティブな部位を自動的に検出し、モザイク（ピクセル化）処理を施すツールを開発します。一般配布を想定し、GUI（グラフィカルユーザーインターフェース）を備えたWindows用実行ファイル（.exe）形式での提供を目指します。

## ユーザーレビューが必要な項目

> [!IMPORTANT]
> - **プライバシーと安全性**: 本ツールはローカル環境で動作し、画像データを外部サーバーに送信しません。
> - **実行形式**: Python環境が不要な **Windows用実行ファイル (.exe)** 形式。
> - **GUI搭載**: 直感的に操作できるよう、フォルダ選択や進捗表示を行うGUIを搭載します。

## 提案される変更

### [Component] データ処理・AIエンジン (Python)

#### [NEW] `App/gui.py`
ユーザーインターフェース。
- `CustomTkinter` を使用し、モダンなダークモードUIを提供。
- フォルダ選択、しきい値調整、開始ボタン、ログ表示。

#### [NEW] `App/auto_mosaic.py`
ツールのメイン制御ロジック。
- `gui.py` と連携し、バックグラウンドスレッドで画像処理を実行。

#### [NEW] `App/detector.py`
`NudeNet` を使用した検出ロジック。

#### [NEW] `App/processor.py`
`OpenCV` を使用した画像加工ロジック。

### [Component] 設定・配布

#### [NEW] `requirements.txt`
`nudenet`, `opencv-python`, `customtkinter`, `pyinstaller`

#### [NEW] `build.bat`
PyInstallerを使用して、ツールを一式をexe化するスクリプト。

#### [NEW] `.agent/GEMINI.md`
プロジェクト固有ルールの設定。

---

## GUIモックアップ
![GUI Mockup](file:///C:/Users/urear/.gemini/antigravity/brain/bf0cb945-9ef8-4bf0-8560-16888c892785/automosaic_gui_mockup_1772158869454.png)

## 検証計画
... (以下略)
