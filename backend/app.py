from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from datetime import datetime
import logging
import re
from typing import Dict, Any
import json
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import langdetect

# استيراد الـ crawler
from crawler import SaudiGazetteCrawler

# إعداد الـ logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء Flask app
app = Flask(__name__)
CORS(app)  # للسماح بطلبات من Frontend

# إعداد OpenAI (تحتاج تضع API key في متغير البيئة)
openai.api_key = os.getenv('OPENAI_API_KEY')

# إنشاء crawler instance
crawler = SaudiGazetteCrawler()

class ArticleFetcher:
    """خدمة جلب محتوى المقالات من الروابط"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_article_content(self, url: str) -> str:
        """جلب محتوى المقال من الرابط"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # محاولة العثور على محتوى المقال بطرق متعددة
            content = ""
            
            # الطريقة الأولى: البحث عن article tag
            article_tag = soup.find('article')
            if article_tag:
                # إزالة العناصر غير المرغوبة
                for unwanted in article_tag.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header', 'iframe', 'noscript']):
                    unwanted.decompose()
                content = article_tag.get_text(separator=' ', strip=True)
            
            # الطريقة الثانية: البحث عن div بـ class معين
            if not content:
                content_divs = soup.find_all('div', class_=lambda x: x and any(
                    keyword in str(x).lower() for keyword in ['content', 'article', 'post', 'story', 'body', 'text', 'entry']
                ))
                for div in content_divs:
                    text = div.get_text(separator=' ', strip=True)
                    if len(text) > len(content):
                        content = text
            
            # الطريقة الثالثة: البحث عن main tag
            if not content:
                main_tag = soup.find('main')
                if main_tag:
                    content = main_tag.get_text(separator=' ', strip=True)
            
            # الطريقة الرابعة: البحث عن p tags
            if not content:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            
            # تنظيف النص
            content = re.sub(r'\s+', ' ', content).strip()
            content = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF.,!?;:()\-"]', '', content)
            
            # قطع النص إذا كان طويلاً جداً
            if len(content) > 4000:
                content = content[:4000] + "..."
            
            return content if len(content) > 100 else None
            
        except Exception as e:
            logger.error(f"خطأ في جلب محتوى المقال: {e}")
            return None

class TranslationService:
    """خدمة الترجمة التلقائية"""
    
    def __init__(self):
        self.translator = GoogleTranslator(source='auto', target='ar')
        self.arabic_keywords = ['العربية', 'السعودية', 'الخليج', 'الشرق الأوسط', 'مكة', 'الرياض', 'جدة']
    
    def detect_language(self, text: str) -> str:
        """اكتشاف لغة النص"""
        try:
            # تنظيف النص أولاً
            clean_text = re.sub(r'[^\w\s]', ' ', text)[:100]  # أول 100 حرف فقط للاكتشاف
            
            detected = langdetect.detect(clean_text)
            logger.info(f"اللغة المكتشفة: {detected}")
            return detected
        except Exception as e:
            logger.error(f"خطأ في اكتشاف اللغة: {e}")
            # إذا فشل الاكتشاف، نتحقق من وجود أحرف عربية
            arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
            if len(arabic_chars) > 10:
                return 'ar'
            return 'en'
    
    def translate_to_arabic(self, text: str) -> tuple[str, bool]:
        """ترجمة النص إلى العربية إذا لزم الأمر"""
        try:
            if not text or not text.strip():
                return text, False
            
            detected_lang = self.detect_language(text)
            
            # إذا كان النص عربي أصلاً، لا نترجم
            if detected_lang == 'ar':
                logger.info("النص عربي أصلاً، لا حاجة للترجمة")
                return text, False
            
            logger.info(f"ترجمة النص من {detected_lang} إلى العربية...")
            
            # تقسيم النص إلى أجزاء صغيرة للترجمة
            chunks = self._split_text(text, 4000)  # حد أعلى للـ deep-translator
            translated_chunks = []
            
            for chunk in chunks:
                try:
                    # إنشاء translator جديد لكل chunk
                    translator = GoogleTranslator(source=detected_lang, target='ar')
                    result = translator.translate(chunk)
                    translated_chunks.append(result)
                except Exception as e:
                    logger.warning(f"فشل في ترجمة جزء من النص: {e}")
                    # في حالة الفشل، نحتفظ بالنص الأصلي
                    translated_chunks.append(chunk)
            
            translated_text = ' '.join(translated_chunks)
            logger.info("تم إكمال الترجمة بنجاح")
            return translated_text, True
            
        except Exception as e:
            logger.error(f"خطأ في الترجمة: {e}")
            return text, False
    
    def _split_text(self, text: str, max_length: int) -> list:
        """تقسيم النص إلى أجزاء صغيرة"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = re.split(r'[.!?]', text)
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

class AIService:
    """خدمة الذكاء الاصطناعي للتلخيص مع الترجمة التلقائية"""
    
    def __init__(self):
        self.max_text_length = 8000
        self.article_fetcher = ArticleFetcher()
        self.translation_service = TranslationService()
        
    def _clean_text(self, text: str) -> str:
        """تنظيف النص من العناصر غير المرغوبة"""
        # إزالة HTML tags إذا وجدت
        text = re.sub(r'<[^>]+>', '', text)
        # إزالة الأسطر الفارغة الزائدة
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # إزالة المسافات الزائدة
        text = re.sub(r'\s+', ' ', text).strip()
        # إزالة الأحرف الخاصة المشكوك فيها
        text = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF.,!?;:()\-"»«]', '', text)
        return text
    
    def _validate_input(self, text: str) -> tuple[bool, str]:
        """فحص صحة النص المدخل"""
        if not text or not text.strip():
            return False, "النص فارغ"
        
        if len(text) > self.max_text_length:
            return False, f"النص طويل جداً. الحد الأقصى {self.max_text_length} حرف"
        
        if len(text.strip()) < 30:
            return False, "النص قصير جداً للتلخيص"
        
        return True, "النص صالح"
    
    def _generate_simple_summary(self, text: str) -> str:
        """توليد ملخص بسيط بدون AI APIs - محسن"""
        try:
            # تنظيف النص أولاً
            cleaned_text = self._clean_text(text)
            
            # تقسيم النص إلى جمل
            sentences = re.split(r'[.!?؟]+', cleaned_text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 40]
            
            if len(sentences) == 0:
                return "لم يتمكن من استخراج ملخص مفيد من النص المعطى."
            
            # تحديد عدد الجمل للملخص بناءً على طول النص
            if len(sentences) <= 3:
                summary_sentences = sentences
            elif len(sentences) <= 8:
                # أول جملتين وآخر جملتين
                summary_sentences = sentences[:2] + sentences[-2:]
            else:
                # أول جملة، جملتين من الوسط، آخر جملة
                mid_start = len(sentences) // 3
                mid_end = 2 * len(sentences) // 3
                summary_sentences = [sentences[0]] + sentences[mid_start:mid_start+2] + [sentences[-1]]
            
            # إنشاء الملخص
            summary = '. '.join(summary_sentences)
            if not summary.endswith('.'):
                summary += '.'
            
            # التأكد من أن الملخص ليس قصيراً جداً
            if len(summary) < 150 and len(sentences) > 3:
                # إضافة جملة أخرى إذا كان الملخص قصير
                if len(sentences) >= 5:
                    summary = '. '.join(sentences[:4]) + '.'
            
            return summary
            
        except Exception as e:
            logger.error(f"خطأ في التلخيص البسيط: {e}")
            return "حدث خطأ في عملية التلخيص. يرجى المحاولة مرة أخرى."
    
    def _extract_content_from_article_data(self, article_data: Dict) -> str:
        """استخراج المحتوى من بيانات المقال"""
        try:
            # جمع النص المتاح من بيانات المقال
            content_parts = []
            
            if article_data.get('title'):
                content_parts.append(article_data['title'])
            
            if article_data.get('excerpt') and article_data['excerpt'] != "No excerpt available":
                content_parts.append(article_data['excerpt'])
            
            # محاولة جلب المحتوى الكامل من الرابط
            if article_data.get('link'):
                logger.info(f"محاولة جلب محتوى المقال من: {article_data['link']}")
                full_content = self.article_fetcher.fetch_article_content(article_data['link'])
                if full_content:
                    content_parts.append(full_content)
                    logger.info("تم جلب محتوى المقال بنجاح")
                else:
                    logger.warning("فشل في جلب محتوى المقال من الرابط")
            
            combined_content = '\n\n'.join(content_parts)
            return combined_content if len(combined_content.strip()) > 50 else None
            
        except Exception as e:
            logger.error(f"خطأ في استخراج محتوى المقال: {e}")
            return None
    
    def summarize_to_arabic(self, text: str, is_article_data: bool = False) -> Dict[str, Any]:
        """
        تلخيص النص إلى العربية مع الترجمة التلقائية
        
        Args:
            text: النص المراد تلخيصه أو JSON string لبيانات المقال
            is_article_data: هل النص عبارة عن بيانات مقال
            
        Returns:
            dict: يحتوي على الملخص بالعربية أو رسالة خطأ
        """
        try:
            # إذا كان النص عبارة عن بيانات مقال
            actual_text = text
            if is_article_data:
                try:
                    article_data = json.loads(text) if isinstance(text, str) else text
                    extracted_content = self._extract_content_from_article_data(article_data)
                    if extracted_content:
                        actual_text = extracted_content
                    else:
                        return {
                            "success": False,
                            "error": "لم يتمكن من استخراج محتوى كافٍ للتلخيص",
                            "summary_ar": None
                        }
                except Exception as e:
                    logger.error(f"خطأ في معالجة بيانات المقال: {e}")
                    actual_text = text
            
            # تنظيف وفحص النص
            cleaned_text = self._clean_text(actual_text)
            
            # الترجمة التلقائية إلى العربية إذا لزم الأمر
            translated_text, was_translated = self.translation_service.translate_to_arabic(cleaned_text)
            
            # استخدام النص المترجم للتلخيص
            final_text = translated_text
            
            is_valid, validation_message = self._validate_input(final_text)
            
            if not is_valid:
                return {
                    "success": False,
                    "error": validation_message,
                    "summary_ar": None,
                    "was_translated": was_translated
                }
            
            summary = None
            method_used = "Unknown"
            
            # المحاولة 1: OpenAI GPT
            if openai.api_key and openai.api_key.strip():
                try:
                    logger.info("محاولة التلخيص باستخدام OpenAI...")
                    
                    system_prompt = """أنت خبير في تلخيص النصوص الإخبارية باللغة العربية. 
                    مهمتك هي قراءة النص المعطى وكتابة ملخص شامل ودقيق باللغة العربية الفصحى.

                    متطلبات الملخص:
                    1. يجب أن يكون باللغة العربية الفصحى
                    2. يجب أن يغطي النقاط الرئيسية في النص
                    3. يجب أن يكون واضحاً ومفهوماً
                    4. يجب أن يتراوح طوله بين 150-300 كلمة
                    5. يجب أن يحافظ على المعنى الأساسي للنص الأصلي
                    6. تجنب التفاصيل الصغيرة والتركيز على الأهم
                    7. اكتب بأسلوب صحفي واضح ومباشر
                    8. استخدم جمل كاملة وتراكيب سليمة"""
                    
                    user_prompt = f"الرجاء تلخيص هذا النص باللغة العربية:\n\n{final_text}"
                    
                    response = openai.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        max_tokens=400,
                        temperature=0.7
                    )
                    
                    summary = response.choices[0].message.content.strip()
                    method_used = "OpenAI GPT-4"
                    logger.info("تم التلخيص بنجاح باستخدام OpenAI")
                    
                except Exception as e:
                    logger.error(f"فشل OpenAI: {e}")
                    summary = None
            
            # إذا لم يتوفر OpenAI أو فشل، استخدم التلخيص البسيط
            if not summary:
                logger.info("استخدام التلخيص البسيط...")
                summary = self._generate_simple_summary(final_text)
                method_used = "Simple Summary Algorithm"
            
            return {
                "success": True,
                "summary_ar": summary,
                "original_length": len(text),
                "summary_length": len(summary),
                "method_used": method_used,
                "was_translated": was_translated,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في التلخيص: {e}")
            return {
                "success": False,
                "error": f"خطأ في خدمة التلخيص: {str(e)}",
                "summary_ar": None
            }

# إنشاء AI service instance
ai_service = AIService()

@app.route('/')
def health_check():
    """فحص حالة الخادم"""
    return jsonify({
        "status": "running",
        "message": "Saudi Gazette Article Summarizer API with Auto Translation",
        "version": "2.0",
        "features": [
            "Article Crawling",
            "Auto Translation to Arabic",
            "AI-Powered Summarization",
            "Enhanced UI"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/crawler/articles', methods=['GET'])
def get_articles():
    """
    GET /crawler/articles
    إرجاع قائمة المقالات من Saudi Gazette
    """
    try:
        # فحص إذا كان المستخدم يريد إجبار التحديث
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        
        # جلب المقالات
        articles = crawler.fetch_articles(force_refresh=force_refresh)
        
        return jsonify({
            "success": True,
            "articles": articles,
            "count": len(articles),
            "last_update": crawler.last_update.isoformat() if crawler.last_update else None,
            "cache_valid": crawler._is_cache_valid()
        })
        
    except Exception as e:
        logger.error(f"خطأ في جلب المقالات: {e}")
        return jsonify({
            "success": False,
            "error": "خطأ في جلب المقالات",
            "articles": []
        }), 500

@app.route('/articles/summarize', methods=['POST'])
def summarize_article():
    """
    POST /articles/summarize
    تلخيص النص المرسل إلى العربية مع الترجمة التلقائية
    
    Request body: {"text": "النص المراد تلخيصه"} أو {"article": {article_data}}
    Response: {"summary_ar": "الملخص بالعربية", "was_translated": boolean}
    """
    try:
        # فحص Content-Type
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type يجب أن يكون application/json"
            }), 400
        
        # الحصول على البيانات
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "البيانات مفقودة"
            }), 400
        
        # التحقق من نوع البيانات
        if 'article' in data:
            # تلخيص مقال محدد
            article_data = data['article']
            result = ai_service.summarize_to_arabic(json.dumps(article_data), is_article_data=True)
        elif 'text' in data:
            # تلخيص نص مخصص
            text = data.get('text', '').strip()
            if not text:
                return jsonify({
                    "success": False,
                    "error": "حقل 'text' مطلوب ولا يمكن أن يكون فارغاً"
                }), 400
            
            result = ai_service.summarize_to_arabic(text)
        else:
            return jsonify({
                "success": False,
                "error": "يجب إرسال 'text' أو 'article'"
            }), 400
        
        if not result["success"]:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400
        
        # إرجاع الملخص
        return jsonify({
            "success": True,
            "summary_ar": result["summary_ar"],
            "was_translated": result.get("was_translated", False),
            "metadata": {
                "original_length": result.get("original_length"),
                "summary_length": result.get("summary_length"),
                "method_used": result.get("method_used"),
                "timestamp": result.get("timestamp")
            }
        })
        
    except Exception as e:
        logger.error(f"خطأ في endpoint التلخيص: {e}")
        return jsonify({
            "success": False,
            "error": "خطأ داخلي في الخادم"
        }), 500

@app.errorhandler(404)
def not_found(error):
    """معالج الصفحات غير الموجودة"""
    return jsonify({
        "success": False,
        "error": "الصفحة غير موجودة"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """معالج الأخطاء الداخلية"""
    return jsonify({
        "success": False,
        "error": "خطأ داخلي في الخادم"
    }), 500

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Saudi Gazette Article Summarizer API v2.0")
    print("🔥 NEW: Auto Translation to Arabic!")
    print("=" * 80)
    print("📡 Endpoints:")
    print("  GET  /                     - Health check")
    print("  GET  /crawler/articles     - Get articles from Saudi Gazette")
    print("  POST /articles/summarize   - Summarize text to Arabic (with auto translation)")
    print("=" * 80)
    print("🔧 Environment variables (optional):")
    print("  OPENAI_API_KEY - للتلخيص المتقدم باستخدام GPT-4")
    print("=" * 80)
    print("✨ NEW FEATURES:")
    print("  🌍 Auto Translation: English → Arabic")
    print("  🧠 Enhanced AI Summarization")
    print("  🎨 Improved UI Components")
    print("  🔍 Better Content Extraction")
    print("=" * 80)
    print("💡 التلخيص سيعمل حتى بدون API keys مع ترجمة تلقائية!")
    print("=" * 80)
    app.run(debug=True, host='0.0.0.0', port=5000)