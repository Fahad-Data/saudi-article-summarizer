# ملخص الأخبار السعودي بالذكاء الاصطناعي

تطبيق ويب متكامل يقوم بجلب المقالات من صحيفة الجازيت السعودية وتلخيصها باستخدام الذكاء الاصطناعي مع الترجمة التلقائية.

## نظرة عامة

يوفر هذا التطبيق خدمة تلخيص الأخبار من صحيفة الجازيت السعودية باستخدام تقنيات الذكاء الاصطناعي المتقدمة. يدعم التطبيق الترجمة التلقائية من أي لغة إلى العربية مع واجهة مستخدم عصرية ومتجاوبة.

## الميزات الرئيسية

**الذكاء الاصطناعي**
- تلخيص متقدم باستخدام GPT-4 مع خيار التشغيل بدون API keys
- ترجمة تلقائية من أي لغة إلى العربية
- معالجة ذكية للنصوص العربية والإنجليزية

**جلب المقالات**
- crawler متقدم لجلب المقالات من Saudi Gazette
- نظام cache ذكي لتوفير الأداء
- معالجة قوية لتغيرات هيكل الموقع

**واجهة المستخدم**
- تصميم عصري متجاوب مع جميع الشاشات
- تأثيرات بصرية تفاعلية
- دعم كامل للغة العربية من اليمين إلى اليسار

**الأداء والموثوقية**
- Docker containers للنشر السهل
- معالجة الأخطاء المتقدمة
- Health checks ومراقبة الخدمات

## هيكل المشروع

```
saudi-article-summarizer/
├── backend/
│   ├── app.py              # Flask API الرئيسي
│   ├── crawler.py          # خدمة جلب المقالات
│   ├── requirements.txt    # متطلبات Python
│   └── Dockerfile          # Docker للـ backend
├── frontend/
│   ├── index.html          # الواجهة الأمامية
│   ├── nginx.conf          # إعدادات Nginx
│   └── Dockerfile          # Docker للـ frontend
├── docker-compose.yml      # تشغيل الخدمات
├── .env.example           # متغيرات البيئة
└── README.md              # هذا الملف
```

## متطلبات التشغيل

- Docker و Docker Compose
- معرف API من OpenAI اختياري

## خطوات التشغيل

### الخطوة الأولى: تحضير البيئة

```bash
# استنساخ المشروع
git clone <repository-url>
cd saudi-article-summarizer

# نسخ ملف المتغيرات
cp .env.example .env
```

### الخطوة الثانية: إعداد متغيرات البيئة اختياري

قم بتعديل ملف .env وأضف معرف OpenAI API إذا كان متوفراً:
```
OPENAI_API_KEY=sk-your-api-key-here
```

### الخطوة الثالثة: تشغيل التطبيق

```bash
# بناء وتشغيل الحاويات
docker-compose up --build

# للتشغيل في الخلفية
docker-compose up -d --build
```

### الخطوة الرابعة: الوصول للتطبيق

- الواجهة الأمامية: http://localhost
- API الخلفي: http://localhost:5000
- فحص صحة الخادم: http://localhost:5000/

## واجهات البرمجة

### GET /
فحص حالة الخادم

### GET /crawler/articles
جلب المقالات الحديثة من صحيفة الجازيت

**المعاملات:**
- `force_refresh` اختياري: فرض تحديث المقالات

**الاستجابة:**
```json
{
  "success": true,
  "articles": [...],
  "count": 8,
  "last_update": "2024-01-01T10:00:00",
  "cache_valid": true
}
```

### POST /articles/summarize
تلخيص النص أو المقال

**محتوى الطلب:**
```json
{
  "text": "النص المراد تلخيصه"
}
```
أو:
```json
{
  "article": {
    "title": "عنوان المقال",
    "link": "رابط المقال",
    "excerpt": "مقتطف"
  }
}
```

**الاستجابة:**
```json
{
  "success": true,
  "summary_ar": "الملخص باللغة العربية",
  "was_translated": false,
  "metadata": {
    "method_used": "OpenAI GPT-4",
    "timestamp": "2024-01-01T10:00:00"
  }
}
```

## اختبار التطبيق

### اختبار API باستخدام curl

```bash
# فحص حالة الخادم
curl http://localhost:5000/

# جلب المقالات
curl http://localhost:5000/crawler/articles

# تلخيص نص
curl -X POST http://localhost:5000/articles/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "هذا نص تجريبي للتلخيص..."}'
```

### اختبار باستخدام Postman

1. اختبر endpoints المختلفة
2. تحقق من استجابات JSON
3. اختبر التلخيص مع نصوص بلغات مختلفة

## أوامر Docker

```bash
# بناء الحاويات
docker-compose build

# تشغيل الخدمات
docker-compose up -d

# عرض الحاويات العاملة
docker-compose ps

# عرض السجلات
docker-compose logs -f

# إيقاف الخدمات
docker-compose down
```

## استكشاف الأخطاء

### خطأ في الاتصال بـ API
```bash
# تحقق من أن Backend يعمل
docker-compose logs backend

# تحقق من المنافذ
netstat -tlnp | grep :5000
```

### مشاكل الترجمة
```bash
# تحقق من مكتبة deep-translator
pip install deep-translator==1.11.4
```

### مشاكل CORS
- تأكد من إعدادات CORS في Flask
- تحقق من proxy في Nginx

## المراقبة

### فحص صحة الخدمات
```bash
# فحص صحة Backend
curl http://localhost:5000/

# فحص صحة Frontend
curl http://localhost/
```

### عرض السجلات
```bash
# عرض جميع السجلات
docker-compose logs

# سجلات خدمة محددة
docker-compose logs backend
docker-compose logs frontend
```

## التطوير المحلي

### Backend Flask

```bash
cd backend

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل الخادم
python app.py
```

### Frontend للتطوير

```bash
cd frontend

# تشغيل خادم بسيط للتطوير
python -m http.server 8080
```

## الأمان

### إعدادات الإنتاج
- لا تحفظ API keys في ملفات .env العامة
- استخدم secrets management للمفاتيح الحساسة
- فعل security headers في Nginx

### Rate Limiting
- محدود حالياً على مستوى التطبيق
- يمكن إضافة nginx rate limiting للإنتاج

## الدعم الفني

للمساعدة والدعم:
- إنشاء Issue في GitHub
- مراجعة الوثائق
- فحص السجلات للأخطاء

---

**تم تطويره بواسطة:** فهد العمودي