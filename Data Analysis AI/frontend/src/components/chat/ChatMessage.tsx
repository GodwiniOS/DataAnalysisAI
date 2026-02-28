import React from 'react';
import { Terminal, BarChart3, Info, AlertOctagon, CheckCircle2, User, Database } from 'lucide-react';

interface ChatMessageProps {
    role: 'user' | 'assistant';
    content: any;
    type?: 'text' | 'code' | 'chart' | 'error' | 'success' | 'analysis_result' | 'insight' | 'clarification';
    options?: string[];
    stats?: any[];
}

const RichText = ({ text }: { text: string }) => {
    if (!text) return null;

    // Split by patterns: **bold** or `code`
    const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);

    return (
        <span className="inline leading-relaxed">
            {parts.map((part, i) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                    const val = part.slice(2, -2);
                    return (
                        <span key={i} className="inline-flex items-center px-1.5 py-0.5 mx-0.5 rounded-md bg-blue-500/10 text-blue-400 font-bold border border-blue-500/20 shadow-sm transition-all hover:scale-105 cursor-default group whitespace-nowrap">
                            <BarChart3 size={10} className="mr-1 opacity-50 group-hover:opacity-100 transition-opacity" />
                            {val}
                        </span>
                    );
                }
                if (part.startsWith('`') && part.endsWith('`')) {
                    const col = part.slice(1, -1);
                    return (
                        <button
                            key={i}
                            onClick={() => {
                                // Potentially trigger a column focus in the future
                                window.dispatchEvent(new CustomEvent('focus-column', { detail: col }));
                            }}
                            className="inline-flex items-center px-2 py-0.5 mx-0.5 rounded-full bg-zinc-800 text-zinc-300 font-mono text-[11px] border border-zinc-700 hover:border-blue-500 hover:text-blue-400 transition-all shadow-sm"
                        >
                            <Terminal size={10} className="mr-1.5 opacity-40" />
                            {col}
                        </button>
                    );
                }
                return <span key={i}>{part}</span>;
            })}
        </span>
    );
};

export const ChatMessage = ({ role, content, type = 'text', options, stats }: ChatMessageProps) => {
    const isUser = role === 'user';

    return (
        <div className={`flex gap-4 p-6 ${isUser ? '' : 'bg-zinc-900/40 border-y border-zinc-900'}`}>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-zinc-800' : 'bg-blue-600'
                }`}>
                {isUser ? <User size={18} /> : <span>AI</span>}
            </div>

            <div className="flex-1 space-y-3 overflow-hidden">
                {type === 'code' ? (
                    <div className="rounded-xl overflow-hidden border border-zinc-800 bg-zinc-950">
                        <div className="flex items-center gap-2 px-4 py-2 bg-zinc-900 text-[10px] font-mono text-zinc-500 border-b border-zinc-800">
                            <Terminal size={12} /> pandas_code.py
                        </div>
                        <pre className="p-4 text-xs font-mono text-blue-400 overflow-x-auto">
                            <code>{content}</code>
                        </pre>
                    </div>
                ) : type === 'error' ? (
                    <div className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                        <AlertOctagon size={16} className="mt-0.5" />
                        <span>{content}</span>
                    </div>
                ) : type === 'success' ? (
                    <div className="flex items-start gap-2 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400 text-sm">
                        <CheckCircle2 size={16} className="mt-0.5" />
                        <span>{content}</span>
                    </div>
                ) : type === 'analysis_result' ? (
                    <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl space-y-2">
                        <div className="flex items-center gap-2 text-xs font-semibold text-zinc-500 uppercase tracking-wider">
                            <Info size={14} /> Analysis Result
                        </div>
                        <div className="text-zinc-200 text-lg font-medium">
                            {typeof content === 'object' ? JSON.stringify(content, null, 2) : content}
                        </div>
                    </div>
                ) : type === 'chart' ? (
                    <div className="flex items-center gap-3 p-4 bg-blue-600/10 border border-blue-600/20 rounded-xl text-blue-400">
                        <BarChart3 size={20} />
                        <div>
                            <p className="text-sm font-bold">Chart Generated</p>
                            <p className="text-xs opacity-80">Interactive visualization added to the right panel.</p>
                        </div>
                    </div>
                ) : type === 'clarification' ? (
                    <div className="space-y-4">
                        <div className="text-zinc-300 leading-relaxed font-sans prose prose-invert max-w-none mb-4">
                            {typeof content === 'string' ? content : JSON.stringify(content)}
                        </div>
                        {options && options.length > 0 && (
                            <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-zinc-800/50">
                                <p className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-1">Select an Option to Proceed:</p>
                                {options.map((opt, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => {
                                            window.dispatchEvent(new CustomEvent('fill-chatbox', { detail: opt }));
                                        }}
                                        className="group flex flex-col items-start px-5 py-3 w-full max-w-sm bg-zinc-900 border border-zinc-700 hover:border-blue-500 hover:bg-zinc-800 rounded-xl transition-all shadow-sm"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-6 h-6 rounded-full bg-zinc-800 group-hover:bg-blue-600/20 text-blue-500 flex items-center justify-center text-xs font-bold transition-colors">
                                                {idx + 1}
                                            </div>
                                            <span className="text-sm font-medium text-zinc-300 group-hover:text-blue-400 text-left transition-colors">{opt}</span>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                ) : type === 'insight' || type === 'text' ? (
                    <div className="space-y-4">
                        {/* Stat Cards */}
                        {stats && stats.length > 0 && (
                            <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
                                {stats.map((stat: any, idx: number) => (
                                    <div key={idx} className="p-3 bg-zinc-900 border border-zinc-800 rounded-xl flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-lg bg-blue-600/10 flex items-center justify-center text-blue-500">
                                            {stat.icon === 'rows' && <Database size={16} />}
                                            {stat.icon === 'columns' && <Info size={16} />}
                                            {stat.icon === 'missing' && <AlertOctagon size={16} />}
                                            {stat.icon === 'duplicates' && <CheckCircle2 size={16} />}
                                        </div>
                                        <div>
                                            <p className="text-[10px] text-zinc-500 uppercase font-bold tracking-wider">{stat.label}</p>
                                            <p className="text-sm font-bold text-zinc-200">{stat.value}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="text-zinc-300 leading-relaxed font-sans prose prose-invert max-w-none space-y-3">
                            {(typeof content === 'string' ? content : content?.content || JSON.stringify(content))
                                .split('\n')
                                .map((line: string, idx: number) => {
                                    const trimmed = line.trim();
                                    if (trimmed.startsWith('- ') || trimmed.startsWith('* ') || trimmed.match(/^\d+\.\s/)) {
                                        const content = trimmed.replace(/^[-*]\s|\d+\.\s/, '');
                                        return (
                                            <div key={idx} className="flex gap-2 pl-2 items-start py-0.5">
                                                <div className="w-1.5 h-1.5 rounded-full bg-blue-500/40 mt-1.5 flex-shrink-0" />
                                                <div className="flex-1">
                                                    <RichText text={content} />
                                                </div>
                                            </div>
                                        );
                                    }
                                    return trimmed ? (
                                        <div key={idx} className="mb-4">
                                            <RichText text={trimmed} />
                                        </div>
                                    ) : (
                                        <div key={idx} className="h-2" />
                                    );
                                })}
                        </div>

                        {options && options.length > 0 && (
                            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-zinc-900/50">
                                {options.map((opt, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => {
                                            window.dispatchEvent(new CustomEvent('fill-chatbox', { detail: opt }));
                                        }}
                                        className="px-3 py-1.5 bg-zinc-900/50 hover:bg-blue-600/10 border border-zinc-800 hover:border-blue-500/30 rounded-full text-xs text-zinc-400 hover:text-blue-400 transition-all"
                                    >
                                        {opt}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="text-zinc-300 leading-relaxed font-sans prose prose-invert max-w-none">
                        {typeof content === 'string' ? content : JSON.stringify(content)}
                    </div>
                )}
            </div>
        </div>
    );
};
