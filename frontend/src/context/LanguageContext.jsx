import React, { createContext, useState, useContext, useEffect } from 'react';

const LanguageContext = createContext({
    language: 'en',
    changeLanguage: () => { },
    SUPPORTED_LANGUAGES: []
});

export const SUPPORTED_LANGUAGES = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'sw', name: 'Swahili', flag: '🇹🇿' },
    { code: 'zu', name: 'Zulu', flag: '🇿🇦' },
    { code: 'xh', name: 'Xhosa', flag: '🇿🇦' },
    { code: 'yo', name: 'Yoruba', flag: '🇳🇬' },
    { code: 'ig', name: 'Igbo', flag: '🇳🇬' },
    { code: 'ha', name: 'Hausa', flag: '🇳🇬' },
    { code: 'am', name: 'Amharic', flag: '🇪🇹' },
    { code: 'so', name: 'Somali', flag: '🇸🇴' },
    { code: 'sn', name: 'Shona', flag: '🇿🇼' },
    { code: 'af', name: 'Afrikaans', flag: '🇿🇦' },
    { code: 'om', name: 'Oromo', flag: '🇪🇹' },
    { code: 'rw', name: 'Kinyarwanda', flag: '🇷🇼' },
    { code: 'tw', name: 'Twi', flag: '🇬🇭' },
    { code: 'st', name: 'Sesotho', flag: '🇱🇸' }
];

export const LanguageProvider = ({ children }) => {
    const [language, setLanguage] = useState('en');
    const [translations, setTranslations] = useState({});

    useEffect(() => {
        const savedLang = localStorage.getItem('recapture_language');
        if (savedLang) {
            setLanguage(savedLang);
        }
    }, []);

    // Load translations when language changes
    useEffect(() => {
        const loadTranslations = async () => {
            try {
                // In a real app, we might dynamic import. 
                // For now, we'll assume files exist or fallback to English.
                // We'll start by just loading the current language file.
                // Note: Vite/Webpack dynamic imports work best here.

                let transData;
                try {
                    // Attempt to load the specific language file
                    // This relies on Vite's dynamic import capabilities
                    const module = await import(`../translations/${language}.json`);
                    transData = module.default;
                } catch (e) {
                    console.warn(`Could not load translations for ${language}, falling back to English`);
                    const module = await import(`../translations/en.json`);
                    transData = module.default;
                }
                setTranslations(transData);
            } catch (err) {
                console.error("Failed to load translations:", err);
            }
        };

        loadTranslations();
    }, [language]);

    const changeLanguage = (langCode) => {
        setLanguage(langCode);
        localStorage.setItem('recapture_language', langCode);
    };

    // Translation helper function
    // Supports nested keys like 'dashboard.title'
    const t = (key) => {
        const keys = key.split('.');
        let value = translations;

        for (const k of keys) {
            if (value && value[k] !== undefined) {
                value = value[k];
            } else {
                return key; // Fallback to key if not found
            }
        }

        return value;
    };

    return (
        <LanguageContext.Provider value={{ language, changeLanguage, t, SUPPORTED_LANGUAGES }}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => useContext(LanguageContext);
