
# Smart Traffic Radar (YOLOv8 + ByteTrack + Speed Limit)

- كشف وتتبع سيارات/موتورات
- حساب السرعة لكل Track عبر تحويل pixels->meters
- تنبيه المخالفين لحد السرعة (لون أحمر + ⚠ OVER)
- إخراج فيديو و CSV + ملخص

## Setup
pip install -r requirements.txt

## Run
python app.py
# ثم افتح: http://localhost:5053

## Calibration
- أدخل ppm مباشرة، أو نقطتين + المسافة الحقيقية ليحسب ppm آلياً.
