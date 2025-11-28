import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import { Globe } from 'lucide-react';

const LanguageSelector = () => {
    const { language, changeLanguage, SUPPORTED_LANGUAGES } = useLanguage();

    return (
        <div className="language-selector" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Globe size={18} style={{ color: 'var(--text-secondary)' }} />
            <select
                value={language}
                onChange={(e) => changeLanguage(e.target.value)}
                style={{
                    background: 'transparent',
                    border: '1px solid var(--border)',
                    color: 'var(--text-primary)',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    cursor: 'pointer',
                    outline: 'none'
                }}
            >
                {SUPPORTED_LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                        {lang.flag} {lang.name}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default LanguageSelector;
