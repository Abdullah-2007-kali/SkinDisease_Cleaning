# ===============
# Data Exploration + تنظيف الصور + كشف المكررات
# ===============
import os
import pandas as pd
from PIL import Image, ImageOps
import hashlib

data_path = ""
image_stats = []
corr = 0
hashes = {}
duplicates = []
target_format = "JPEG"
target_size = (224, 224)

# قراءة الكلاسات
classes = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
print(f"Classes: {classes} | Count: {len(classes)}")

for class_name in classes:
    class_path = os.path.join(data_path, class_name)
    images = [f for f in os.listdir(class_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    print(f"Class {class_name}: len: {len(images)}")
    
    for img_name in images:
        img_path = os.path.join(class_path, img_name)

        try:
            with Image.open(img_path) as img:
                width, height = img.size
                mode = img.mode
                
                # حفظ معلومات عن الصورة
                image_stats.append({
                    'class': class_name,
                    'filename': img_name,
                    'width': width,
                    'height': height,
                    'mode': mode,
                    'aspect_ratio': round(width / height, 2) if height != 0 else 0
                })

                # تحويل الصورة لـ RGB
                if img.mode != 'RGB':
                    img = img.convert("RGB")

                # تحسين التباين
                img = ImageOps.autocontrast(img)

                # تغيير الحجم مع الحفاظ على النسبة + إضافة حواف (Padding)
                img.thumbnail(target_size)
                delta_w = target_size[0] - img.width
                delta_h = target_size[1] - img.height
                padding = (delta_w//2, delta_h//2, delta_w - delta_w//2, delta_h - delta_h//2)
                img = ImageOps.expand(img, padding, fill=(0, 0, 0))

                # حفظ الصورة بصيغة موحدة
                new_path = os.path.splitext(img_path)[0] + ".jpg"
                img.save(new_path, format=target_format, quality=95)

            # حساب بصمة الصورة (hash) للكشف عن المكررات
            with open(new_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            if file_hash in hashes:
                duplicates.append((new_path, hashes[file_hash]))
            else:
                hashes[file_hash] = new_path

            # حذف الملف الأصلي لو الصيغة اختلفت
            if new_path != img_path and os.path.exists(img_path):
                os.remove(img_path)

        except Exception as e:
            print(f"⚠️ خطأ في {img_path} | {e}")
            try:
                os.remove(img_path)
                corr += 1
            except:
                pass

# تحويل النتائج إلى DataFrame
df_stats = pd.DataFrame(image_stats)

if not df_stats.empty:
    print(df_stats.describe())
    df_stats.to_csv("image_stats.csv", index=False)
else:
    print("❌ لم يتم جمع أي صور صالحة")

print(f"🗑️ عدد الصور التالفة التي تم حذفها: {corr}")
print(f"📸 عدد الصور المكررة المكتشفة: {len(duplicates)}")
if duplicates:
    print("أمثلة على المكررات:", duplicates[:5])
