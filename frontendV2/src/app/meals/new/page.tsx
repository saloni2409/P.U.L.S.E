'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import AuthLayout from '@/components/layout/AuthLayout'
import { authService } from '@/services/auth'

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

export default function NewMealPage() {
  const router = useRouter()
  const [token, setToken] = useState<string | null>(null)

  // Chat state
  const [chatMessages, setChatMessages] = useState<Message[]>([])
  const [chatMealItems, setChatMealItems] = useState<MealItem[]>([])
  const [nutrition, setNutrition] = useState<any>({})
  const [chatState, setChatState] = useState<ChatState>('COLLECTING')
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [chatEditMode, setChatEditMode] = useState(false)
  const [chatError, setChatError] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [mealType, setMealType] = useState<string | null>(null)
  const [mealTime, setMealTime] = useState<string | null>(null)
  const [showKeyForm, setShowKeyForm] = useState(false)
  const [tempApiKey, setTempApiKey] = useState('')
  const [apiKeyError, setApiKeyError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom for chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  // Get token on mount
  useEffect(() => {
    const tkn = authService.getToken()
    if (!tkn) {
      router.push('/login')
    } else {
      setToken(tkn)
    }
  }, [router])

  // Initialize chat session on mount
  useEffect(() => {
    if (!sessionId && token) {
      initializeChatSession()
    }
  }, [token, sessionId])

  const initializeChatSession = async () => {
    try {
      setChatLoading(true)
      const res = await fetch('/api/meals-ai/chat/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({})  // No meal_type - let it be inferred from conversation
      })

      if (res.ok) {
        const data = await res.json()
        setSessionId(data.session_id)
        setChatState(data.state as ChatState)
        setChatMessages([
          {
            message_id: 'system-init',
            role: 'SYSTEM',
            content: data.message,
            created_at: new Date().toISOString()
          }
        ])
      } else {
        const errorData = await res.json()
        const errorMsg = errorData.detail || 'Failed to start chat'
        if (errorMsg.includes('Gemini') || errorMsg.includes('API key')) {
          setApiKeyError(errorMsg)
          setShowKeyForm(true)
        } else {
          setChatError(errorMsg)
        }
      }
    } catch (err) {
      setChatError('Failed to initialize chat')
    } finally {
      setChatLoading(false)
    }
  }

  const handleSendChatMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!chatInput.trim() || !sessionId) return

    const userMessage = chatInput
    setChatInput('')
    setChatLoading(true)
    setChatError(null)

    try {
      const newUserMsg: Message = {
        message_id: `user-${Date.now()}`,
        role: 'USER',
        content: userMessage,
        created_at: new Date().toISOString()
      }
      setChatMessages(prev => [...prev, newUserMsg])

      const res = await fetch(`/api/meals-ai/chat/send-message/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ message: userMessage })
      })

      if (res.ok) {
        const data = await res.json()

        if (data.message) {
          const assistantMsg: Message = {
            message_id: `assistant-${Date.now()}`,
            role: 'ASSISTANT',
            content: data.message,
            created_at: new Date().toISOString()
          }
          setChatMessages(prev => [...prev, assistantMsg])
        }

        setChatState(data.state as ChatState)
        setChatMealItems(data.meal_items || [])
        setNutrition(data.nutrition || {})

        if (data.state === 'CONFIRMING') {
          loadChatSummary()
        }
      } else {
        const error = await res.json()
        setChatError(error.detail || 'Failed to send message')
      }
    } catch (err) {
      setChatError('Failed to send message')
    } finally {
      setChatLoading(false)
    }
  }

  const loadChatSummary = async () => {
    if (!sessionId) return

    try {
      const res = await fetch(`/api/meals-ai/chat/summary/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })

      if (res.ok) {
        const data = await res.json()
        setChatMealItems(data.meal_items || [])
        setNutrition(data.nutrition || {})
        setChatState(data.state as ChatState)
        setMealType(data.meal_type)
        setMealTime(data.meal_time)
      }
    } catch (err) {
      console.error('Failed to load summary:', err)
    }
  }

  const handleUpdateChatMealItem = (index: number, field: string, value: any) => {
    const updated = [...chatMealItems]
    updated[index] = { ...updated[index], [field]: value }
    setChatMealItems(updated)
  }

  const handleRemoveChatItem = (index: number) => {
    setChatMealItems(chatMealItems.filter((_, i) => i !== index))
  }

  const handleAddChatItem = () => {
    setChatMealItems([
      ...chatMealItems,
      { food_name: '', quantity: 1, unit: 'pieces', calories: 0 }
    ])
  }

  const handleSaveChatMeal = async () => {
    if (!sessionId) return

    try {
      setChatLoading(true)

      let res = await fetch(`/api/meals-ai/chat/meal-items/${sessionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ meal_items: chatMealItems })
      })

      if (!res.ok) {
        const error = await res.json()
        setChatError(error.detail || 'Failed to update meal items')
        return
      }

      res = await fetch(`/api/meals-ai/chat/save/${sessionId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })

      if (res.ok) {
        setChatState('SAVED')
        router.push('/meals')
      } else {
        const error = await res.json()
        setChatError(error.detail || 'Failed to save meal')
      }
    } catch (err) {
      setChatError('Failed to save meal')
    } finally {
      setChatLoading(false)
    }
  }

  const handleCancelChat = async () => {
    if (!sessionId) return

    try {
      setChatLoading(true)
      const res = await fetch(`/api/meals-ai/chat/cancel/${sessionId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })

      if (res.ok) {
        router.push('/meals')
      }
    } catch (err) {
      setChatError('Failed to cancel')
    } finally {
      setChatLoading(false)
    }
  }

  const handleSaveApiKey = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!tempApiKey.trim()) {
      setApiKeyError('API key cannot be empty')
      return
    }

    try {
      setChatLoading(true)
      setApiKeyError(null)
      
      const res = await fetch('/api/user/gemini-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ api_key: tempApiKey })
      })

      if (res.ok) {
        setTempApiKey('')
        setShowKeyForm(false)
        // Try to initialize chat again
        initializeChatSession()
      } else {
        const errorData = await res.json()
        setApiKeyError(errorData.detail || 'Failed to save API key')
      }
    } catch (err) {
      setApiKeyError('Failed to save API key')
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <AuthLayout title="Log a Meal">
      <div className="max-w-6xl mx-auto">
        {/* Single Chat Window */}
        <div className="bg-white rounded-xl shadow overflow-hidden flex flex-col h-[600px]">
          {/* Chat Header */}
          <div className="bg-neutral-50 border-b border-neutral-200 px-6 py-4 flex justify-between items-center">
            <div>
              <h2 className="text-lg font-semibold text-neutral-900">Log Your Meal</h2>
              {mealType && (
                <p className="text-sm text-neutral-600 mt-1">
                  {mealType.charAt(0) + mealType.slice(1).toLowerCase()}
                  {mealTime && ` • ${mealTime}`}
                </p>
              )}
            </div>
            <button
              onClick={handleCancelChat}
              disabled={chatLoading || chatState === 'SAVED'}
              className="px-4 py-2 text-neutral-600 hover:text-neutral-900 disabled:opacity-50 text-sm font-medium"
            >
              Cancel
            </button>
          </div>

          <div className="flex-1 flex gap-6 overflow-hidden">
            {/* Messages Area */}
            <div className="flex-1 flex flex-col border-r border-neutral-200">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {chatMessages.map((msg) => (
                  <div
                    key={msg.message_id}
                    className={`flex ${msg.role === 'USER' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg text-sm ${
                        msg.role === 'USER'
                          ? 'bg-primary-600 text-white'
                          : 'bg-neutral-200 text-neutral-900'
                      }`}
                    >
                      <p>{msg.content}</p>
                    </div>
                  </div>
                ))}

                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="bg-neutral-200 text-neutral-900 px-4 py-3 rounded-lg text-sm">
                      <p>Thinking...</p>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              {chatState !== 'SAVED' && chatState !== 'CANCELLED' && (
                <form onSubmit={handleSendChatMessage} className="border-t border-neutral-200 p-4">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      placeholder="Tell me what you ate..."
                      disabled={chatLoading}
                      className="flex-1 px-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
                    />
                    <button
                      type="submit"
                      disabled={chatLoading || !chatInput.trim()}
                      className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 text-sm font-medium"
                    >
                      Send
                    </button>
                  </div>
                </form>
              )}
            </div>

            {/* Sidebar - Meal Items & Nutrition */}
            <div className="w-80 bg-neutral-50 overflow-y-auto">
              <div className="p-6 space-y-6">
                {/* Meal Items */}
                <div>
                  <h3 className="text-sm font-semibold text-neutral-900 mb-4">Meal Items</h3>
                  <div className="space-y-3">
                    {chatMealItems.map((item, idx) => (
                      <div key={idx} className="bg-white p-3 rounded-lg space-y-2 border border-neutral-200">
                        <input
                          type="text"
                          value={item.food_name}
                          onChange={(e) =>
                            handleUpdateChatMealItem(idx, 'food_name', e.target.value)
                          }
                          placeholder="Food name"
                          disabled={!chatEditMode}
                          className="w-full px-2 py-1 text-xs border border-neutral-300 rounded disabled:bg-neutral-50"
                        />
                        <div className="flex gap-2">
                          <input
                            type="number"
                            value={item.quantity}
                            onChange={(e) =>
                              handleUpdateChatMealItem(idx, 'quantity', parseFloat(e.target.value))
                            }
                            placeholder="Qty"
                            disabled={!chatEditMode}
                            className="flex-1 px-2 py-1 text-xs border border-neutral-300 rounded disabled:bg-neutral-50"
                          />
                          <select
                            value={item.unit}
                            onChange={(e) =>
                              handleUpdateChatMealItem(idx, 'unit', e.target.value)
                            }
                            disabled={!chatEditMode}
                            className="flex-1 px-2 py-1 text-xs border border-neutral-300 rounded disabled:bg-neutral-50"
                          >
                            <option>pieces</option>
                            <option>grams</option>
                            <option>cups</option>
                            <option>ml</option>
                          </select>
                        </div>
                        {chatEditMode && (
                          <button
                            onClick={() => handleRemoveChatItem(idx)}
                            className="w-full text-xs text-danger-600 hover:text-danger-700 p-1"
                          >
                            Remove
                          </button>
                        )}
                      </div>
                    ))}
                  </div>

                  {chatEditMode && (
                    <button
                      onClick={handleAddChatItem}
                      className="w-full mt-3 px-4 py-2 text-xs bg-neutral-200 text-neutral-900 rounded-lg hover:bg-neutral-300 font-medium"
                    >
                      + Add Item
                    </button>
                  )}

                  {chatState === 'CONFIRMING' && (
                    <div className="mt-4 flex gap-2">
                      <button
                        onClick={() => setChatEditMode(!chatEditMode)}
                        className="flex-1 px-4 py-2 text-xs bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium"
                      >
                        {chatEditMode ? 'Done Editing' : 'Edit'}
                      </button>
                      <button
                        onClick={handleSaveChatMeal}
                        disabled={chatLoading}
                        className="flex-1 px-4 py-2 text-xs bg-success-600 text-white rounded-lg hover:bg-success-700 disabled:opacity-50 font-medium"
                      >
                        Save Meal
                      </button>
                    </div>
                  )}
                </div>

                {/* Nutrition */}
                {nutrition.totals && (
                  <div>
                    <h3 className="text-sm font-semibold text-neutral-900 mb-2">Nutrition Summary</h3>
                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span className="text-neutral-600">Calories:</span>
                        <span className="font-semibold">{Math.round(nutrition.totals.calories)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-600">Protein:</span>
                        <span className="font-semibold">{nutrition.totals.protein?.toFixed(1)}g</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-600">Carbs:</span>
                        <span className="font-semibold">{nutrition.totals.carbs?.toFixed(1)}g</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-600">Fat:</span>
                        <span className="font-semibold">{nutrition.totals.fat?.toFixed(1)}g</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Error Alert */}
          {chatError && (
            <div className="bg-danger-50 border-t border-danger-200 px-6 py-3">
              <div className="flex justify-between items-center">
                <p className="text-sm text-danger-800">{chatError}</p>
                <button
                  onClick={() => setChatError(null)}
                  className="text-xs text-danger-600 hover:text-danger-700 font-medium"
                >
                  Dismiss
                </button>
              </div>
            </div>
          )}
        </div>

        {/* API Key Form Modal */}
        {showKeyForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
              <h2 className="text-lg font-bold text-neutral-900 mb-4">Gemini API Key Required</h2>
              <p className="text-sm text-neutral-600 mb-4">
                {apiKeyError || 'Please provide your Gemini API key to use the chat feature.'}
              </p>
              
              <form onSubmit={handleSaveApiKey} className="space-y-4">
                <div>
                  <label htmlFor="apiKey" className="block text-sm font-medium text-neutral-700 mb-2">
                    API Key
                  </label>
                  <input
                    type="password"
                    id="apiKey"
                    value={tempApiKey}
                    onChange={(e) => setTempApiKey(e.target.value)}
                    placeholder="Enter your Gemini API key"
                    className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    disabled={chatLoading}
                  />
                  <p className="text-xs text-neutral-500 mt-2">
                    Get your key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Google AI Studio</a>
                  </p>
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowKeyForm(false)
                      setTempApiKey('')
                      setApiKeyError(null)
                    }}
                    disabled={chatLoading}
                    className="flex-1 px-4 py-2 border border-neutral-300 text-neutral-700 rounded-lg hover:bg-neutral-50 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={chatLoading || !tempApiKey.trim()}
                    className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                  >
                    {chatLoading ? 'Saving...' : 'Save Key'}
                  </button>
                </div>

                {apiKeyError && (
                  <div className="bg-danger-50 border border-danger-200 rounded p-3">
                    <p className="text-xs text-danger-800">{apiKeyError}</p>
                  </div>
                )}
              </form>
            </div>
          </div>
        )}
      </div>
    </AuthLayout>
  )
}
