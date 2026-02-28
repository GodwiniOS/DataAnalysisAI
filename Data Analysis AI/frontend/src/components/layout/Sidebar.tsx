import React from 'react';
import { Database, MessageSquare, History, Settings, Plus, Book } from 'lucide-react';
import { useDatasetStore } from '@/store/useDatasetStore';

export const Sidebar = () => {
    const { profile, reset, activeTab, setActiveTab } = useDatasetStore();

    return (
        <div className="w-64 bg-zinc-950 border-r border-zinc-900 flex flex-col h-full">
            <div className="p-6">
                <div className="flex items-center gap-3 mb-8">
                    <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-600/20">
                        <Database className="text-white" size={20} />
                    </div>
                    <div>
                        <h1 className="font-bold text-white tracking-tight">Data Lab</h1>
                        <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold">Intelligence</p>
                    </div>
                </div>

                <div className="space-y-1">
                    <button
                        onClick={() => reset()}
                        className="w-full flex items-center gap-3 px-3 py-2 text-zinc-400 hover:text-white hover:bg-zinc-900 rounded-lg transition-all text-sm group"
                    >
                        <Plus className="group-hover:rotate-90 transition-transform" size={18} />
                        New session
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-6">
                <div>
                    <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3 px-2">
                        Active Dataset
                    </h3>
                    {profile ? (
                        <div className="flex items-center gap-2 p-2 bg-blue-600/10 text-blue-400 rounded-lg border border-blue-600/20 text-sm">
                            <Database size={16} />
                            <span className="truncate">{profile.filename || 'Untitled.csv'}</span>
                        </div>
                    ) : (
                        <p className="text-xs text-zinc-600 px-2 italic">No dataset uploaded</p>
                    )}
                </div>

                <div>
                    <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3 px-2">
                        Menu
                    </h3>
                    <nav className="space-y-1 px-2">
                        {[
                            { icon: MessageSquare, label: 'Chat', active: activeTab === 'table' || activeTab === 'chart', action: () => setActiveTab('table') },
                            { icon: Book, label: 'Documentation', active: activeTab === 'docs', action: () => setActiveTab('docs') },
                            { icon: History, label: 'History' },
                            { icon: Settings, label: 'Settings' },
                        ].map((item) => (
                            <button
                                key={item.label}
                                onClick={item.action}
                                className={`flex items-center gap-2 w-full p-2 rounded-lg text-sm transition-colors ${item.active ? 'bg-zinc-800 text-white font-medium border border-zinc-700/50 shadow-sm' : 'text-zinc-400 hover:text-white hover:bg-zinc-900'
                                    }`}
                            >
                                <item.icon size={16} /> {item.label}
                            </button>
                        ))}
                    </nav>
                </div>
            </div>

            <div className="mt-auto pt-4 border-t border-zinc-900">
                <div className="flex items-center gap-3 px-2">
                    <div className="w-8 h-8 bg-zinc-800 rounded-full flex items-center justify-center">
                        <span className="text-xs font-medium">GU</span>
                    </div>
                    <div>
                        <p className="text-xs font-medium text-white">Guest User</p>
                        <p className="text-[10px] text-zinc-500">Free Tier</p>
                    </div>
                </div>
            </div>
        </div>
    );
};
