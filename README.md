## ParkingLotAnnotTool
駐車場のアノテーションツール

* 駐車場の固定カメラでの撮影動画を入力できる
* 車室の矩形を設定できる
* 動画から、時間的に一定間隔で、車室の矩形の形状に画像を切り出せる
* 切り出した時間的に連続な画像を、在/空のいずれかに分類できる
* 分類した結果から、json形式のGround Truthを作成できる

## Get started

```bash
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```