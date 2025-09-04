# Saudi Article Summarizer

> ملخص الأخبار السعودي بالذكاء الاصطناعي مع ترجمة تلقائية

## 📖 نظرة عامة

تطبيق ويب متكامل يقوم بجلب المقالات من صحيفة الجزيرة السعودية وتلخيصها باستخدام الذكاء الاصطناعي. يدعم الترجمة التلقائية من أي لغة إلى العربية مع واجهة مستخدم عصرية ومتجاوبة.

## ✨ الميزات

### 🤖 **الذكاء الاصطناعي**
- تلخيص متقدم باستخدام GPT-4 (مع خيار التشغيل بدون API keys)
- ترجمة تلقائية من أي لغة إلى العربية
- معالجة ذكية للنصوص العربية والإنجليزية

### 🔍 **جلب المقالات**
- crawler متقدم لجلب المقالات من Saudi Gazette
- نظام cache ذكي لتوفير الأداء
- معالجة قوية لتغيرات هيكل الموقع

### 🎨 **واجهة المستخدم**
- تصميم عصري وأنيق بألوان داكنة
- متجاوب بالكامل مع جميع الشاشات
- تأثيرات بصرية تفاعلية
- دعم كامل للغة العربية (RTL)

### 🚀 **الأداء والموثوقية**
- Docker containers للنشر السهل
- معالجة الأخطاء المتقدمة
- Redis caching (اختياري)
- Health checks وmonitoring

## 🏗️ المعمارية

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

## 🚀 التثبيت والتشغيل

### المتطلبات الأساسية
- Docker و Docker Compose
- Python 3.11+ (للتطوير المحلي)
- معرف API من OpenAI (اختياري)

### 1. تحضير المشروع

```bash
# استنساخ المشروع
git clone <repository-url>
cd saudi-article-summarizer

# إنشاء هيكل المجلدات
mkdir -p backend frontend

# نقل الملفات
mv app.py crawler.py requirements.txt backend/
mv index.html nginx.conf backend/Dockerfile frontend/
mv frontend/Dockerfile frontend/
```

### 2. إعداد متغيرات البيئة

```bash
# نسخ ملف المتغيرات
cp .env.example .env

# تعديل المتغيرات
nano .env
```

أضف معرف OpenAI API (اختياري):
```
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. التشغيل باستخدام Docker

```bash
# بناء وتشغيل الحاويات
docker-compose up --build

# أو التشغيل في الخلفية
docker-compose up -d --build
```

### 4. الوصول للتطبيق

- **الواجهة الأمامية**: http://localhost
- **API**: http://localhost:5000
- **Health Check**: http://localhost:5000/

## 🔧 التطوير المحلي

### Backend (Flask)

```bash
cd backend

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل الخادم
python app.py
```

### Frontend (تطوير)

```bash
cd frontend

# تشغيل خادم بسيط للتطوير
python -m http.server 8080
# أو
npx serve .
```

## 📡 واجهات البرمجة (API)

### GET /
فحص حالة الخادم

### GET /crawler/articles
جلب المقالات الحديثة

**Parameters:**
- `force_refresh` (optional): فرض تحديث المقالات

**Response:**
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

**Request Body:**
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

**Response:**
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

## 🧪 الاختبار

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

1. استورد ملف collection (إذا وُجد)
2. اختبر endpoints المختلفة
3. تحقق من استجابات JSON

## 🐳 Docker Commands

```bash
# بناء الحاويات
docker-compose build

# تشغيل الخدمات
docker-compose up -d

# عرض الحاويات العاملة
docker-compose ps

# عرض logs
docker-compose logs -f

# إيقاف الخدمات
docker-compose down

# إزالة كل شيء (البيانات أيضاً)
docker-compose down -v --rmi all
```

## 🔧 المشاكل الشائعة

### خطأ في الاتصال بـ API
```bash
# تحقق من أن Backend يعمل
docker-compose logs backend

# تحقق من المنافذ
netstat -tlnp | grep :5000
```

### مشاكل CORS
- تأكد من إعدادات CORS في Flask
- تحقق من proxy في Nginx

### مشاكل الترجمة
```bash
# تحقق من مكتبة deep-translator
pip install deep-translator==1.11.4

# اختبار الترجمة يدوياً
python -c "from deep_translator import GoogleTranslator; print(GoogleTranslator(source='en', target='ar').translate('Hello'))"
```

## 📊 المراقبة والصيانة

### Health Checks
```bash
# فحص صحة Backend
curl http://localhost:5000/

# فحص صحة Frontend
curl http://localhost/

# فحص صحة Redis
docker exec redis redis-cli ping
```

### Logs
```bash
# عرض جميع logs
docker-compose logs

# logs لخدمة محددة
docker-compose logs backend
docker-compose logs frontend
```

## 🔒 الأمان

### إعدادات الإنتاج

1. **متغيرات البيئة:**
   ```bash
   # لا تُبقِ API keys في .env
   # استخدم secrets management
   ```

2. **Nginx Security Headers:**
   - X-Frame-Options
   - X-Content-Type-Options
   - X-XSS-Protection

3. **Rate Limiting:**
   - محدود حالياً على مستوى التطبيق
   - يمكن إضافة nginx rate limiting

## 🚀 النشر للإنتاج

### على AWS/Azure/GCP

1. إنشاء VM instances
2. تثبيت Docker و Docker Compose
3. نسخ المشروع ومتغيرات البيئة
4. تشغيل `docker-compose up -d`
5. إعداد Load Balancer و SSL

### باستخدام Docker Swarm

```bash
# تهيئة swarm
docker swarm init

# نشر stack
docker stack deploy -c docker-compose.yml saudi-summarizer
```

## 🤝 المساهمة

1. Fork المشروع
2. إنشاء feature branch
3. Commit التغييرات
4. Push للـ branch
5. إنشاء Pull Request

## 📝 التحديثات المستقبلية

- [ ] دعم قواعد البيانات (PostgreSQL)
- [ ] نظام المستخدمين والمصادقة
- [ ] API Rate Limiting متقدم
- [ ] دعم مصادر أخبار إضافية
- [ ] Mobile App (React Native/Flutter)
- [ ] Advanced Analytics Dashboard

## 📄 الترخيص

هذا المشروع مرخص تحت [MIT License](LICENSE).

## 🆘 الدعم

للمساعدة والدعم:
- إنشاء Issue في GitHub
- مراجعة documentations
- فحص logs للأخطاء

---


**تم إنشاؤه بواسطة:** فهد العمودي 
