import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, PlusCircle, Square } from 'lucide-react';
import { useDatasetStore } from '@/store/useDatasetStore';
import { ChatMessage } from './ChatMessage';

export const ChatArea = () => {
    const [input, setInput] = useState('');
    const {
        messages,
        addMessage,
        isLoading,
        setLoading,
        loadingStep,
        setLoadingStep,
        sessionId,
        setPreview,
        setProfile,
        setActiveChart,
        suggestedPrompts,
        setSuggestedPrompts,
        llmProvider,
        llmModel,
        abortController,
        setAbortController
    } = useDatasetStore();
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    useEffect(() => {
        const handleFill = (e: any) => {
            if (e.detail) {
                setInput(e.detail);
            }
        };
        window.addEventListener('fill-chatbox', handleFill);
        return () => window.removeEventListener('fill-chatbox', handleFill);
    }, []);

    const stopGeneration = () => {
        if (abortController) {
            abortController.abort();
            setAbortController(null);
            setLoading(false);
            setLoadingStep('');
            addMessage({
                role: 'assistant',
                content: 'Analysis stopped by user.',
                type: 'error'
            });
        }
    };

    const sendMessage = async (text: string) => {
        if (!text.trim() || isLoading || !sessionId) return;

        const controller = new AbortController();
        setAbortController(controller);

        setInput('');
        addMessage({ role: 'user', content: text, type: 'text' });
        setLoading(true);
        setLoadingStep('🔍 Routing Intent...');

        try {
            const response = await fetch('http://127.0.0.1:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                signal: controller.signal,
                body: JSON.stringify({
                    session_id: sessionId,
                    message: text,
                    provider: llmProvider,
                    model: llmModel
                }),
            });

            const data = await response.json();

            if (data.response) {
                data.response.forEach((element: any) => {
                    if (element.type === 'chart') {
                        setActiveChart(element.content);
                    }
                    addMessage({
                        role: 'assistant',
                        content: element.content,
                        type: element.type as any,
                        options: element.options,
                        stats: element.stats
                    });
                });
            }

            if (data.preview) setPreview(data.preview);
            if (data.profile) setProfile(data.profile);
            if (data.suggested_prompts) setSuggestedPrompts(data.suggested_prompts);

        } catch (err: any) {
            if (err.name === 'AbortError') {
                console.log('Fetch aborted');
            } else {
                addMessage({
                    role: 'assistant',
                    content: "I'm sorry, I encountered an error connecting to the backend. Please ensure the server is running.",
                    type: 'error'
                });
            }
        } finally {
            setLoading(false);
            setLoadingStep('');
            setAbortController(null);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        sendMessage(input);
    };

    return (
        <div className="flex-1 flex flex-col h-full bg-zinc-950 relative">
            <div ref={scrollRef} className="flex-1 overflow-y-auto custom-scrollbar">
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center p-8 text-center">
                        <div className="w-12 h-12 bg-blue-600/10 rounded-2xl flex items-center justify-center mb-6 border border-blue-600/20">
                            <Sparkles size={24} className="text-blue-500" />
                        </div>
                        <h2 className="text-2xl font-bold bg-gradient-to-r from-white to-zinc-500 bg-clip-text text-transparent mb-2">
                            Ready to analyze?
                        </h2>
                        <p className="text-zinc-500 text-sm max-w-sm">
                            Ask me to clean data, perform calculations, or create beautiful visualizations.
                        </p>
                    </div>
                ) : (
                    <div className="pb-60">
                        {messages.map((msg, i) => (
                            <ChatMessage key={i} {...msg} />
                        ))}
                        {isLoading && (
                            <div className="p-6 flex gap-4 animate-pulse bg-zinc-900/20">
                                <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center">
                                    <Sparkles size={14} className="text-zinc-500" />
                                </div>
                                <div className="space-y-3 flex-1 pt-1">
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '300ms' }} />
                                        <span className="text-xs font-medium text-blue-400 ml-2 tracking-wide uppercase">
                                            {loadingStep || 'AI is thinking...'}
                                        </span>
                                    </div>
                                    <div className="h-2.5 bg-zinc-800 rounded w-5/6" />
                                    <div className="h-2.5 bg-zinc-800 rounded w-4/6" />
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-zinc-950 via-zinc-950/90 to-transparent">
                {suggestedPrompts.length > 0 && !isLoading && messages.length <= 1 && (
                    <div className="max-w-3xl mx-auto mb-4 flex flex-wrap gap-2 justify-center">
                        {suggestedPrompts.slice(0, 3).map((prompt, i) => (
                            <button
                                key={i}
                                onClick={() => sendMessage(prompt)}
                                className="px-3 py-1.5 bg-zinc-900/50 hover:bg-blue-600/10 border border-zinc-800 hover:border-blue-500/30 rounded-full text-xs text-zinc-400 hover:text-blue-400 transition-all"
                            >
                                {prompt}
                            </button>
                        ))}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative group">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-teal-500 rounded-2xl opacity-20 group-focus-within:opacity-40 blur transition-all" />
                    <div className="relative flex flex-col bg-zinc-900 border border-zinc-800 rounded-2xl p-2 gap-2">
                        <div className="flex items-center gap-2 px-2 pt-1 border-b border-zinc-800/50 pb-2 mb-1">
                            <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold ml-1">AI Engine</span>
                            <div className="flex bg-zinc-950 p-1 rounded-lg border border-zinc-800/50">
                                {[
                                    { id: 'openai', label: 'GPT-4o', model: 'gpt-4o' },
                                    { id: 'gemini', label: 'Gemini 1.5', model: 'gemini-1.5-flash' },
                                    { id: 'ollama', label: 'DeepSeek (Local)', model: 'deepseek-r1:8b' },
                                    { id: 'llama', label: 'Llama 3', model: 'llama3' }
                                ].map((engine) => (
                                    <button
                                        key={engine.id}
                                        type="button"
                                        onClick={() => useDatasetStore.getState().setLLMSettings(engine.id, engine.model)}
                                        className={`px-2 py-1 text-[10px] rounded-md transition-all ${llmProvider === engine.id
                                            ? 'bg-blue-600 text-white shadow-sm'
                                            : 'text-zinc-500 hover:text-zinc-300'
                                            }`}
                                    >
                                        {engine.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="flex items-center gap-2 pl-2">
                            <PlusCircle className="text-zinc-500 cursor-pointer hover:text-zinc-300" size={20} />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder={`Ask ${llmProvider === 'ollama' ? 'Local Llama' : 'AI'} anything about your data...`}
                                className="flex-1 bg-transparent border-none focus:ring-0 text-sm text-zinc-100 placeholder:text-zinc-600 py-2"
                            />
                            {isLoading ? (
                                <button
                                    type="button"
                                    onClick={stopGeneration}
                                    className="p-2 rounded-xl bg-red-600/20 text-red-500 hover:bg-red-600/30 transition-all border border-red-600/30"
                                >
                                    <Square size={18} fill="currentColor" />
                                </button>
                            ) : (
                                <button
                                    type="submit"
                                    disabled={!input.trim() || isLoading}
                                    className={`p-2 rounded-xl transition-all ${input.trim() && !isLoading ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' : 'bg-zinc-800 text-zinc-600'
                                        }`}
                                >
                                    <Send size={18} />
                                </button>
                            )}
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
};
