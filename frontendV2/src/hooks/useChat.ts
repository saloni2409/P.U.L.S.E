import { useState, useCallback } from 'react';

export type Message = {
  message_id: string;
  role: 'USER' | 'ASSISTANT' | 'SYSTEM';
  content: string;
  created_at: string;
};

export type MealItem = {
  food_name: string;
  quantity: number;
  unit: string;
  calories?: number;
};

export type ChatState = 'COLLECTING' | 'CONFIRMING' | 'SAVED' | 'CANCELLED';

export type ChatSession = {
  session_id: string;
  user_id: string;
  meal_type: string;
  state: ChatState;
  message?: string;
  meal_items?: MealItem[];
  nutrition?: any;
};

export function useChat(initialSessionId?: string) {
  const [sessionId, setSessionId] = useState<string | null>(initialSessionId || null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [mealItems, setMealItems] = useState<MealItem[]>([]);
  const [nutrition, setNutrition] = useState<any>({});
  const [state, setState] = useState<ChatState>('COLLECTING');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startSession = useCallback(
    async (mealType: string, token: string): Promise<ChatSession | null> => {
      try {
        setLoading(true);
        setError(null);

        const res = await fetch('/api/meals-ai/chat/start', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ meal_type: mealType }),
        });

        if (!res.ok) {
          const error = await res.json();
          throw new Error(error.detail || 'Failed to start chat');
        }

        const data = await res.json() as ChatSession;
        setSessionId(data.session_id);
        setState(data.state);

        if (data.message) {
          const systemMsg: Message = {
            message_id: `system-${Date.now()}`,
            role: 'SYSTEM',
            content: data.message,
            created_at: new Date().toISOString(),
          };
          setMessages([systemMsg]);
        }

        return data;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to start chat';
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const sendMessage = useCallback(
    async (message: string, token: string) => {
      if (!sessionId) return null;

      try {
        setLoading(true);
        setError(null);

        // Add user message optimistically
        const userMsg: Message = {
          message_id: `user-${Date.now()}`,
          role: 'USER',
          content: message,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, userMsg]);

        const res = await fetch(`/api/meals-ai/chat/send-message/${sessionId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ message }),
        });

        if (!res.ok) {
          const error = await res.json();
          throw new Error(error.detail || 'Failed to send message');
        }

        const data = await res.json();

        // Add assistant response
        if (data.message) {
          const assistantMsg: Message = {
            message_id: `assistant-${Date.now()}`,
            role: 'ASSISTANT',
            content: data.message,
            created_at: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, assistantMsg]);
        }

        setState(data.state);
        if (data.meal_items) {
          setMealItems(data.meal_items);
        }
        if (data.nutrition) {
          setNutrition(data.nutrition);
        }

        return data;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to send message';
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [sessionId]
  );

  const loadMessages = useCallback(
    async (token: string) => {
      if (!sessionId) return;

      try {
        const res = await fetch(`/api/meals-ai/chat/messages/${sessionId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (res.ok) {
          const data = await res.json() as Message[];
          setMessages(data);
        }
      } catch (err) {
        console.error('Failed to load messages:', err);
      }
    },
    [sessionId]
  );

  const getSummary = useCallback(
    async (token: string) => {
      if (!sessionId) return null;

      try {
        const res = await fetch(`/api/meals-ai/chat/summary/${sessionId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (res.ok) {
          const data = await res.json();
          setMealItems(data.meal_items || []);
          setNutrition(data.nutrition || {});
          setState(data.state);
          return data;
        }
      } catch (err) {
        console.error('Failed to load summary:', err);
      }

      return null;
    },
    [sessionId]
  );

  const updateMealItems = useCallback(
    async (items: MealItem[], token: string) => {
      if (!sessionId) return null;

      try {
        setLoading(true);

        const res = await fetch(`/api/meals-ai/chat/meal-items/${sessionId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ meal_items: items }),
        });

        if (!res.ok) {
          const error = await res.json();
          throw new Error(error.detail || 'Failed to update meal items');
        }

        setMealItems(items);
        return await res.json();
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to update meal items';
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [sessionId]
  );

  const saveMeal = useCallback(
    async (token: string) => {
      if (!sessionId) return null;

      try {
        setLoading(true);

        const res = await fetch(`/api/meals-ai/chat/save/${sessionId}`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          const error = await res.json();
          throw new Error(error.detail || 'Failed to save meal');
        }

        setState('SAVED');
        return await res.json();
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to save meal';
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [sessionId]
  );

  const cancelSession = useCallback(
    async (token: string) => {
      if (!sessionId) return null;

      try {
        setLoading(true);

        const res = await fetch(`/api/meals-ai/chat/cancel/${sessionId}`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          const error = await res.json();
          throw new Error(error.detail || 'Failed to cancel session');
        }

        setState('CANCELLED');
        return await res.json();
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to cancel session';
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [sessionId]
  );

  return {
    sessionId,
    messages,
    mealItems,
    nutrition,
    state,
    loading,
    error,
    startSession,
    sendMessage,
    loadMessages,
    getSummary,
    updateMealItems,
    saveMeal,
    cancelSession,
    setError,
  };
}
