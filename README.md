## ParkingLotAnnotTool
駐車場のアノテーションツール

固定カメラで撮影した駐車場の映像を入力として、
* 車室の座標(四角形を作る画像上の4点)を定義できる
* 座標を定義した車室について、映像中で在車/空車が切り替わるタイミングを記録できる
* 上記の情報をjsonファイルで保存できる

## Get started

```bash
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```