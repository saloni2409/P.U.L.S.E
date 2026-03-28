'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { authService } from '@/services/auth';

type Message = {
  message_id: string;
  role: 'USER' | 'ASSISTANT' | 'SYSTEM';
  content: string;
  created_at: string;
};

type MealItem = {
  food_name: string;
  quantity: number;
  unit: string;
  calories?: number;
};

type ChatState = 'COLLECTING' | 'CONFIRMING' | 'SAVED' | 'CANCELLED';

export default function ChatPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const mealType = searchParams.get('meal_type') || 'BREAKFAST';
  const sessionIdParam = searchParams.get('session_id');
  
  const [token, setToken] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(sessionIdParam);
  const [messages, setMessages] = useState<Message[]>([]);
  const [mealItems, setMealItems] = useState<MealItem[]>([]);
  const [nutrition, setNutrition] = useState<any>({});
  const [state, setState] = useState<ChatState>('COLLECTING');
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiKeyError, setApiKeyError] = useState<string | null>(null);
  const [showKeyForm, setShowKeyForm] = useState(false);
  const [tempApiKey, setTempApiKey] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Get token on mount
  useEffect(() => {
    const tkn = authService.getToken();
    if (!tkn) {
      router.push('/login');
    } else {
      setToken(tkn);
    }
  }, [router]);
  
  // Initialize session
  useEffect(() => {
    if (!sessionId && token) {
      initializeSession();
    }
  }, [sessionId, token]);
  
  // Load messages when session changes
  useEffect(() => {
    if (sessionId && token) {
      loadMessages();
    }
  }, [sessionId, token]);
  
  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const initializeSession = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/meals-ai/chat/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ meal_type: mealType })
      });
      
      if (res.ok) {
        const data = await res.json();
        setSessionId(data.session_id);
        setState(data.state as ChatState);
        
        // Add initial system message
        setMessages([
          {
            message_id: 'system-init',
            role: 'SYSTEM',
            content: data.message,
            created_at: new Date().toISOString()
          }
        ]);
        
        router.push(`?meal_type=${mealType}&session_id=${data.session_id}`);
      } else {
        const errorData = await res.json();
        const errorMsg = errorData.detail || 'Failed to start chat';
        if (errorMsg.includes('Gemini') || errorMsg.includes('API key')) {
          setApiKeyError(errorMsg);
          setShowKeyForm(true);
        } else {
          setError(errorMsg);
        }
      }
    } catch (err) {
      setError('Failed to initialize chat');
    } finally {
      setLoading(false);
    }
  };
  
  const loadMessages = async () => {
    if (!sessionId) return;
    
    try {
      const res = await fetch(`/api/meals-ai/chat/messages/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setMessages(data);
      }
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };
  
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !sessionId) return;
    
    const userMessage = input;
    setInput('');
    setLoading(true);
    setError(null);
    
    try {
      // Add user message to UI
      const newUserMsg: Message = {
        message_id: `user-${Date.now()}`,
        role: 'USER',
        content: userMessage,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, newUserMsg]);
      
      // Send to server
      const res = await fetch(`/api/meals-ai/chat/send-message/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ message: userMessage })
      });
      
      if (res.ok) {
        const data = await res.json();
        
        // Add assistant response
        if (data.message) {
          const assistantMsg: Message = {
            message_id: `assistant-${Date.now()}`,
            role: 'ASSISTANT',
            content: data.message,
            created_at: new Date().toISOString()
          };
          setMessages(prev => [...prev, assistantMsg]);
        }
        
        setState(data.state as ChatState);
        setMealItems(data.meal_items || []);
        setNutrition(data.nutrition || {});
        
        // If state changed to CONFIRMING, load summary
        if (data.state === 'CONFIRMING') {
          loadSummary();
        }
      } else {
        const error = await res.json();
        setError(error.detail || 'Failed to send message');
      }
    } catch (err) {
      setError('Failed to send message');
    } finally {
      setLoading(false);
    }
  };
  
  const loadSummary = async () => {
    if (!sessionId) return;
    
    try {
      const res = await fetch(`/api/meals-ai/chat/summary/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setMealItems(data.meal_items || []);
        setNutrition(data.nutrition || {});
        setState(data.state as ChatState);
      }
    } catch (err) {
      console.error('Failed to load summary:', err);
    }
  };
  
  const handleUpdateMealItem = (index: number, field: string, value: any) => {
    const updated = [...mealItems];
    updated[index] = { ...updated[index], [field]: value };
    setMealItems(updated);
  };
  
  const handleRemoveItem = (index: number) => {
    setMealItems(mealItems.filter((_, i) => i !== index));
  };
  
  const handleAddItem = () => {
    setMealItems([
      ...mealItems,
      { food_name: '', quantity: 1, unit: 'pieces', calories: 0 }
    ]);
  };
  
  const handleSaveMeal = async () => {
    if (!sessionId) return;
    
    try {
      setLoading(true);
      
      // Update meal items first
      let res = await fetch(`/api/meals-ai/chat/meal-items/${sessionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ meal_items: mealItems })
      });
      
      if (!res.ok) {
        const error = await res.json();
        setError(error.detail || 'Failed to update meal items');
        return;
      }
      
      // Save meal
      res = await fetch(`/api/meals-ai/chat/save/${sessionId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        setState('SAVED');
        router.push('/meals');
      } else {
        const error = await res.json();
        setError(error.detail || 'Failed to save meal');
      }
    } catch (err) {
      setError('Failed to save meal');
    } finally {
      setLoading(false);
    }
  };
  
  const handleCancel = async () => {
    if (!sessionId) return;
    
    try {
      setLoading(true);
      const res = await fetch(`/api/meals-ai/chat/cancel/${sessionId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        router.push('/meals');
      }
    } catch (err) {
      setError('Failed to cancel');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveApiKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tempApiKey.trim()) {
      setApiKeyError('API key cannot be empty');
      return;
    }

    try {
      setLoading(true);
      setApiKeyError(null);
      
      const res = await fetch('/api/user/gemini-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ api_key: tempApiKey })
      });

      if (res.ok) {
        setTempApiKey('');
        setShowKeyForm(false);
        // Try to initialize chat again
        initializeSession();
      } else {
        const errorData = await res.json();
        setApiKeyError(errorData.detail || 'Failed to save API key');
      }
    } catch (err) {
      setApiKeyError('Failed to save API key');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">
            Log {mealType.charAt(0) + mealType.slice(1).toLowerCase()}
          </h1>
          <button
            onClick={handleCancel}
            disabled={loading || state === 'SAVED'}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 disabled:opacity-50"
          >
            Cancel
          </button>
        </div>
      </div>
      
      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Chat Messages */}
        <div className="flex-1 flex flex-col border-r border-gray-200">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.message_id}
                className={`flex ${msg.role === 'USER' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    msg.role === 'USER'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{msg.content}</p>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 text-gray-900 px-4 py-2 rounded-lg">
                  <p className="text-sm">Thinking...</p>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Input Area */}
          {state !== 'SAVED' && state !== 'CANCELLED' && (
            <form onSubmit={handleSendMessage} className="border-t border-gray-200 p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type your response..."
                  disabled={loading}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  Send
                </button>
              </div>
            </form>
          )}
        </div>
        
        {/* Sidebar - Meal Items & Nutrition */}
        <div className="w-80 bg-white border-l border-gray-200 overflow-y-auto">
          <div className="p-6 space-y-6">
            {/* Meal Items */}
            <div>
              <h2 className="text-lg font-semibold mb-4">Meal Items</h2>
              <div className="space-y-3">
                {mealItems.map((item, idx) => (
                  <div key={idx} className="bg-gray-50 p-3 rounded-lg space-y-2">
                    <input
                      type="text"
                      value={item.food_name}
                      onChange={(e) =>
                        handleUpdateMealItem(idx, 'food_name', e.target.value)
                      }
                      placeholder="Food name"
                      disabled={!editMode}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded disabled:bg-gray-100"
                    />
                    <div className="flex gap-2">
                      <input
                        type="number"
                        value={item.quantity}
                        onChange={(e) =>
                          handleUpdateMealItem(idx, 'quantity', parseFloat(e.target.value))
                        }
                        placeholder="Qty"
                        disabled={!editMode}
                        className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded disabled:bg-gray-100"
                      />
                      <select
                        value={item.unit}
                        onChange={(e) =>
                          handleUpdateMealItem(idx, 'unit', e.target.value)
                        }
                        disabled={!editMode}
                        className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded disabled:bg-gray-100"
                      >
                        <option>pieces</option>
                        <option>grams</option>
                        <option>cups</option>
                        <option>ml</option>
                      </select>
                    </div>
                    {editMode && (
                      <button
                        onClick={() => handleRemoveItem(idx)}
                        className="w-full text-sm text-red-600 hover:text-red-700 p-1"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                ))}
              </div>
              
              {editMode && (
                <button
                  onClick={handleAddItem}
                  className="w-full mt-3 px-4 py-2 text-sm bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300"
                >
                  + Add Item
                </button>
              )}
              
              {state === 'CONFIRMING' && (
                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => setEditMode(!editMode)}
                    className="flex-1 px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    {editMode ? 'Done Editing' : 'Edit'}
                  </button>
                  <button
                    onClick={handleSaveMeal}
                    disabled={loading}
                    className="flex-1 px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                  >
                    Save Meal
                  </button>
                </div>
              )}
            </div>
            
            {/* Nutrition */}
            {nutrition.totals && (
              <div>
                <h3 className="font-semibold mb-2">Nutrition Summary</h3>
                <div className="space-y-1 text-sm">
                  <p>Calories: <span className="font-semibold">{nutrition.totals.calories}</span></p>
                  <p>Protein: <span className="font-semibold">{nutrition.totals.protein?.toFixed(1)}g</span></p>
                  <p>Carbs: <span className="font-semibold">{nutrition.totals.carbs?.toFixed(1)}g</span></p>
                  <p>Fat: <span className="font-semibold">{nutrition.totals.fat?.toFixed(1)}g</span></p>
                </div>
              </div>
            )}
            
            {/* Session State */}
            <div className="pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-600">
                <strong>State:</strong> {state}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Error Alert */}
      {error && (
        <div className="fixed bottom-6 right-6 bg-red-50 border border-red-200 rounded-lg p-4 max-w-sm">
          <p className="text-sm text-red-800">{error}</p>
          <button
            onClick={() => setError(null)}
            className="mt-2 text-xs text-red-600 hover:text-red-700"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* API Key Form Modal */}
      {showKeyForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Gemini API Key Required</h2>
            <p className="text-sm text-gray-600 mb-4">
              {apiKeyError || 'Please provide your Gemini API key to use the chat feature.'}
            </p>
            
            <form onSubmit={handleSaveApiKey} className="space-y-4">
              <div>
                <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-2">
                  API Key
                </label>
                <input
                  type="password"
                  id="apiKey"
                  value={tempApiKey}
                  onChange={(e) => setTempApiKey(e.target.value)}
                  placeholder="Enter your Gemini API key"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={loading}
                />
                <p className="text-xs text-gray-500 mt-2">
                  Get your key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google AI Studio</a>
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowKeyForm(false);
                    setTempApiKey('');
                    setApiKeyError(null);
                  }}
                  disabled={loading}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading || !tempApiKey.trim()}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Saving...' : 'Save Key'}
                </button>
              </div>

              {apiKeyError && (
                <div className="bg-red-50 border border-red-200 rounded p-3">
                  <p className="text-xs text-red-800">{apiKeyError}</p>
                </div>
              )}
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
