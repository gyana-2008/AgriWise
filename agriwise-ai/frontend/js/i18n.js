/**
 * 🌾 AGRIWISE AI - Multilingual Localization Engine
 * Supports English, Hindi (हिंदी), and Punjabi (ਪੰਜਾਬੀ).
 */

const AgriI18n = {
  translations: {},
  currentLang: localStorage.getItem('agriwise_lang') || 'en',

  async init() {
    await this.loadLocale(this.currentLang);
    this.applyTranslations();
  },

  async loadLocale(lang) {
    try {
      const res = await fetch(`/locales/${lang}.json`);
      if (res.ok) {
        this.translations = await res.json();
        this.currentLang = lang;
        localStorage.setItem('agriwise_lang', lang);
      }
    } catch (e) {
      console.warn(`Could not load locale ${lang}:`, e);
    }
  },

  t(key, fallback = "") {
    return this.translations[key] || fallback || key;
  },

  applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (this.translations[key]) {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          el.placeholder = this.translations[key];
        } else {
          el.innerText = this.translations[key];
        }
      }
    });

    // Update language select dropdown value if present
    const selector = document.getElementById('langSelect');
    if (selector) {
      selector.value = this.currentLang;
    }
  },

  async switchLanguage(lang) {
    await this.loadLocale(lang);
    this.applyTranslations();
  }
};

window.AgriI18n = AgriI18n;
document.addEventListener('DOMContentLoaded', () => {
  AgriI18n.init();
});
