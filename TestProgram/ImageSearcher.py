'''
画像検索トレーニングプログラム
ターゲット画像のの中にテンプレート画像と一致する画像を検索する。
ターゲット内の画像と一致した部分を赤線で囲む
一致した部分をOCRで文字列に変換する。空白文字を削除してテキストに表示させる

環境設定メモ；
1,Python3 install
2,pipのInstallとアップグレードをTerminalで実行する。
    $ py -m pip install --upgrade pip
3,OpenCV install(main/extra)
    $ pip install opencv-python
    拡張モジュール(extra)も必要な場合
    $ pip install opencv-contrib-python
4,OCRツールTesseract install
    $ pip install pytesseract
5,PIL
    PIL更新がされていない古いもの、Pillowが代替のライブラリー
    ただし、pipに両方の同時インストールはできない。
    $ pip list でインストール確認すること。

    $ pip install pillow
'''

import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
import tkinter as tk
from tkinter import filedialog

class ImageSearcher:
    def __init__(self, target_path, template_path):
        self.target_path = target_path
        self.template_path = template_path

        self.target_img = cv2.imread(self.target_path)
        self.template_img = cv2.imread(self.template_path)

        # OCRを使用するための設定
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def search(self, threshold=0.8):
        # テンプレート画像を読み込む
        template_img = cv2.imread(self.template_path)

        # テンプレートマッチングを実行する
        res = cv2.matchTemplate(self.target_img, template_img, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        results = []
        for pt in zip(*loc[::-1]):
            # テンプレート画像の位置に赤い枠線を描画する
            target_img_copy = self.target_img.copy()
            cv2.rectangle(target_img_copy, pt, (pt[0] + template_img.shape[1], pt[1] + template_img.shape[0]), (0, 0, 255), 2)

            # テンプレート画像の部分を切り取る
            cropped_img = self.target_img[pt[1]:pt[1] + template_img.shape[0], pt[0]:pt[0] + template_img.shape[1]]

            # OCRで文字列に変換する
            text = pytesseract.image_to_string(Image.fromarray(cropped_img), lang='jpn')
            # 空白文字を削除する
            text = text.replace(' ', '').replace('\n', '')

            results.append((pt, text, target_img_copy))

        return results


if __name__ == '__main__':
    # 実行中のプログラムファイルのパスを取得
    file_path = os.path.abspath(__file__)

    # ファイルが存在するディレクトリーのパスを取得
    dir_path = os.path.dirname(file_path)

    # Work_Image フォルダーのパスを取得
    work_image_path = os.path.join(dir_path, 'Work_Image')

    # Work_Image フォルダー内にある Template_ で始まる PNG ファイルのリストを取得する
    template_files = [f for f in os.listdir(work_image_path) if f.startswith('Template_') and f.endswith('.png')]

    # ファイル選択ダイアログを表示する
    root = tk.Tk()
    root.withdraw()
    target_path = filedialog.askopenfilename(title="Select Target Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])

    # ファイルが選択されなかった場合はプログラムを終了する
    if not target_path:
        print("No target image selected. Program terminated.")
        exit()

    for template_file in template_files:
        searcher = ImageSearcher(target_path, os.path.join(work_image_path, template_file))
        results = searcher.search()

        # 認識したテキストを出力する
        for result in results:
            print(f"Template: {template_file}, Text: {result[1]}")

        # 結果の画像を表示する
        for result in results:
            cv2.imshow(f"Template: {template_file}", result[2])
            cv2.waitKey(0)

    cv2.destroyAllWindows()


