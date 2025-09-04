# استخدام Python 3.11 كصورة أساسية
FROM python:3.11-slim

# تحديد مجلد العمل
WORKDIR /app

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت المكتبات المطلوبة
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كامل كود التطبيق
COPY . .

# إنشاء مجلد للـ logs
RUN mkdir -p /app/logs

# تحديد المتغيرات البيئية
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# فتح المنفذ 5000
EXPOSE 5000

# إنشاء مستخدم غير root للأمان
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# تشغيل التطبيق
CMD ["python", "app.py"]