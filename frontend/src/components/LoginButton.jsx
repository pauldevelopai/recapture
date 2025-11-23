import { LogIn } from 'lucide-react';

export default function LoginButton() {
    const handleLogin = () => {
        // Mock login for now
        alert("Google Login integration coming soon! (Requires GCP Client ID)");
    };

    return (
        <button
            onClick={handleLogin}
            style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                width: '100%',
                marginTop: 'auto', // Push to bottom of sidebar
                background: 'var(--surface)',
                border: '1px solid var(--border)',
                color: 'var(--text)',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius)',
                cursor: 'pointer',
                transition: 'all 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--primary)'}
            onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border)'}
        >
            <LogIn size={20} />
            <span>Sign in with Google</span>
        </button>
    );
}
