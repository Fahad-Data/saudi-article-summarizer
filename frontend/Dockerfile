# استخدام Nginx كصورة أساسية
FROM nginx:alpine

# إزالة الصفحة الافتراضية لـ Nginx
RUN rm -rf /usr/share/nginx/html/*

# نسخ ملف HTML إلى مجلد Nginx
COPY index.html /usr/share/nginx/html/

# نسخ إعدادات Nginx المخصصة
COPY nginx.conf /etc/nginx/conf.d/default.conf

# فتح المنفذ 80
EXPOSE 80

# تشغيل Nginx
CMD ["nginx", "-g", "daemon off;"]