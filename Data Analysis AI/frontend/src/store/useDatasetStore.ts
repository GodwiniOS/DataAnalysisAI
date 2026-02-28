import { create } from 'zustand';

interface Message {
    role: 'user' | 'assistant';
    content: any;
    type: 'text' | 'code' | 'chart' | 'error' | 'success' | 'analysis_result' | 'insight' | 'clarification';
    options?: string[]; // Optional array of choices for branching decisions
    stats?: any[];      // NEW: Key stats to highlight
}

interface DatasetState {
    sessionId: string | null;
    profile: any | null;
    preview: any[] | null;
    messages: Message[];
    isLoading: boolean;
    loadingStep: string;
    activeChart: any | null;
    suggestedPrompts: string[];
    llmProvider: string;
    llmModel: string;
    abortController: AbortController | null;
    activeTab: 'table' | 'chart' | 'docs';
    setSessionId: (id: string) => void;
    setProfile: (profile: any) => void;
    setPreview: (preview: any[]) => void;
    setMessages: (messages: Message[]) => void;
    addMessage: (message: Message) => void;
    setLoading: (loading: boolean) => void;
    setLoadingStep: (step: string) => void;
    setActiveChart: (chart: any) => void;
    setSuggestedPrompts: (prompts: string[]) => void;
    setLLMSettings: (provider: string, model: string) => void;
    setAbortController: (ac: AbortController | null) => void;
    setActiveTab: (tab: 'table' | 'chart' | 'docs') => void;
    reset: () => void;
}

export const useDatasetStore = create<DatasetState>((set) => ({
    sessionId: typeof window !== 'undefined' ? localStorage.getItem('ai_data_lab_session') : null,
    profile: null,
    preview: null,
    messages: [],
    isLoading: false,
    loadingStep: '',
    activeChart: null,
    suggestedPrompts: [],
    llmProvider: 'openai',
    llmModel: 'gpt-4o',
    abortController: null,
    activeTab: 'table',
    setSessionId: (id) => {
        localStorage.setItem('ai_data_lab_session', id);
        set({ sessionId: id });
    },
    setProfile: (profile) => set((state) => ({ profile: { ...state.profile, ...profile } })),
    setPreview: (preview) => set({ preview }),
    setMessages: (messages) => set({ messages }),
    addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
    setLoading: (loading) => set({ isLoading: loading }),
    setLoadingStep: (step) => set({ loadingStep: step }),
    setActiveChart: (chart) => set({ activeChart: chart }),
    setSuggestedPrompts: (prompts) => set({ suggestedPrompts: prompts }),
    setLLMSettings: (provider, model) => set({ llmProvider: provider, llmModel: model }),
    setAbortController: (ac) => set({ abortController: ac }),
    setActiveTab: (tab) => set({ activeTab: tab }),
    reset: () => {
        localStorage.removeItem('ai_data_lab_session');
        set({
            sessionId: null,
            profile: null,
            preview: null,
            messages: [],
            isLoading: false,
            activeChart: null,
            suggestedPrompts: []
        });
    },
}));
