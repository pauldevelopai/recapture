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

    useEffect(() => {
        const savedLang = localStorage.getItem('recapture_language');
        if (savedLang) {
            setLanguage(savedLang);
        }
    }, []);

    const changeLanguage = (langCode) => {
        setLanguage(langCode);
        localStorage.setItem('recapture_language', langCode);
    };

    return (
        <LanguageContext.Provider value={{ language, changeLanguage, SUPPORTED_LANGUAGES }}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => useContext(LanguageContext);
