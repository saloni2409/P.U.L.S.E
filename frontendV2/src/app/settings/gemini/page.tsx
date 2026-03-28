'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

type KeyStatus = {
  has_key: boolean;
  last_verified: string | null;
  created_at: string | null;
  setup_required: boolean;
};

export default function GeminiSettingsPage() {
  const router = useRouter();
  const { token } = useAuth();
  
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [hasKey, setHasKey] = useState(false);
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [keyStatus, setKeyStatus] = useState<KeyStatus | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  // Redirect if not authenticated
  useEffect(() => {
    if (!token) {
      router.push('/login');
    } else {
      checkKeyStatus();
    }
  }, [token, router]);
  
  const checkKeyStatus = async () => {
    try {
      const res = await fetch('/api/user/gemini-key/status', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setKeyStatus(data);
        setHasKey(data.has_key);
      }
    } catch (error) {
      console.error('Failed to check key status:', error);
      setMessage({ type: 'error', text: 'Failed to check key status' });
    }
  };
  
  const handleSaveKey = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!apiKey.trim()) {
      setMessage({ type: 'error', text: 'Please enter an API key' });
      return;
    }
    
    setLoading(true);
    setMessage(null);
    
    try {
      const res = await fetch('/api/user/gemini-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ api_key: apiKey })
      });
      
      if (res.ok) {
        const data = await res.json();
        setMessage({ type: 'success', text: data.message });
        setHasKey(true);
        setApiKey('');
        await checkKeyStatus();
      } else {
        const error = await res.json();
        setMessage({ 
          type: 'error', 
          text: error.detail || 'Failed to save API key' 
        });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save API key' });
    } finally {
      setLoading(false);
    }
  };
  
  const handleDeleteKey = async () => {
    if (!confirm('Are you sure you want to delete your Gemini API key? You will need to set a new one to use chat features.')) {
      return;
    }
    
    setLoading(true);
    setMessage(null);
    
    try {
      const res = await fetch('/api/user/gemini-key', {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setMessage({ type: 'success', text: data.message });
        setHasKey(false);
        await checkKeyStatus();
      } else {
        const error = await res.json();
        setMessage({ 
          type: 'error', 
          text: error.detail || 'Failed to delete API key' 
        });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to delete API key' });
    } finally {
      setLoading(false);
    }
  };
  
  const handleVerifyKey = async () => {
    setVerifying(true);
    setMessage(null);
    
    try {
      const res = await fetch('/api/user/gemini-key/verify', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        if (data.valid) {
          setMessage({ type: 'success', text: data.message });
          await checkKeyStatus();
        } else {
          setMessage({ type: 'error', text: data.message });
        }
      } else {
        setMessage({ type: 'error', text: 'Verification failed' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to verify API key' });
    } finally {
      setVerifying(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          Gemini API Settings
        </h1>
        
        {/* Message Alert */}
        {message && (
          <div
            className={`mb-4 p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-50 border border-green-200'
                : 'bg-red-50 border border-red-200'
            }`}
          >
            <p
              className={`text-sm ${
                message.type === 'success' ? 'text-green-800' : 'text-red-800'
              }`}
            >
              {message.text}
            </p>
          </div>
        )}
        
        {hasKey && keyStatus ? (
          /* Key is set */
          <div className="space-y-4">
            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
              <p className="text-green-800 font-medium mb-2">
                ✅ Gemini API Key Configured
              </p>
              <p className="text-sm text-green-600 mb-2">
                Your API key is securely stored and encrypted.
              </p>
              {keyStatus.last_verified && (
                <p className="text-xs text-green-600">
                  Last verified: {new Date(keyStatus.last_verified).toLocaleDateString()}
                </p>
              )}
              {keyStatus.created_at && (
                <p className="text-xs text-green-600">
                  Created: {new Date(keyStatus.created_at).toLocaleDateString()}
                </p>
              )}
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={handleVerifyKey}
                disabled={verifying || loading}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
              >
                {verifying ? 'Verifying...' : 'Verify Key'}
              </button>
              <button
                onClick={handleDeleteKey}
                disabled={loading || verifying}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 transition"
              >
                {loading ? 'Deleting...' : 'Delete Key'}
              </button>
            </div>
            
            <div className="bg-blue-50 p-3 rounded-lg text-xs text-blue-700">
              <p className="mb-2 font-medium">💰 Billing</p>
              <p>
                All API calls use your personal Google Cloud account. You are responsible for any charges incurred.
              </p>
            </div>
          </div>
        ) : (
          /* Key not set */
          <form onSubmit={handleSaveKey} className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <p className="text-sm text-blue-800 mb-3 font-medium">
                🔑 How to get your Gemini API Key:
              </p>
              <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
                <li>Visit <a href="https://aistudio.google.com/" target="_blank" rel="noopener noreferrer" className="underline font-medium">aistudio.google.com</a></li>
                <li>Click "Get API Key"</li>
                <li>Create or select a project</li>
                <li>Click "Create API Key"</li>
                <li>Copy your new API key</li>
                <li>Paste it below</li>
              </ol>
            </div>
            
            <div className="space-y-2">
              <label htmlFor="api-key" className="block text-sm font-medium text-gray-700">
                Gemini API Key
              </label>
              <div className="relative">
                <input
                  id="api-key"
                  type={showKey ? 'text' : 'password'}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="AIza..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-10"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowKey(!showKey)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showKey ? '🙈' : '👁️'}
                </button>
              </div>
            </div>
            
            <div className="space-y-2 bg-gray-50 p-3 rounded-lg text-xs text-gray-600">
              <p className="font-medium">🔒 Security & Privacy</p>
              <ul className="space-y-1 list-disc list-inside">
                <li>Your key is encrypted with AES-256</li>
                <li>Never stored in plaintext</li>
                <li>Only you can use your key</li>
                <li>Can be deleted anytime</li>
              </ul>
            </div>
            
            <button
              type="submit"
              disabled={!apiKey.trim() || loading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium"
            >
              {loading ? 'Saving...' : 'Save API Key'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
