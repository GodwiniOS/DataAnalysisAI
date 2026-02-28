"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { ChatArea } from '@/components/chat/ChatArea';
import { DynamicPanel } from '@/components/data/DynamicPanel';
import { useDatasetStore } from '@/store/useDatasetStore';
import { Upload, FileType, CheckCircle, ShieldAlert } from 'lucide-react';

export default function Home() {
    const { setSessionId, setProfile, setPreview, setLoading, loadingStep, setLoadingStep, sessionId, isLoading, setMessages, setSuggestedPrompts } = useDatasetStore();
    const [dragActive, setDragActive] = useState(false);
    const [mounted, setMounted] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        const restoreSession = async () => {
            if (sessionId) {
                setLoading(true);
                setLoadingStep('🔄 Restoring Session...');
                try {
                    const response = await fetch(`http://127.0.0.1:8000/sessions/${sessionId}`);
                    if (response.ok) {
                        const data = await response.json();
                        setMessages(data.messages);
                        if (data.preview) setPreview(data.preview);
                        if (data.profile) setProfile(data.profile);
                    } else {
                        // Session might have been cleared from backend but not localStorage
                        console.error("Failed to restore session");
                    }
                } catch (err) {
                    console.error("Error restoring session:", err);
                } finally {
                    setLoading(false);
                }
            }
        };
        restoreSession();
    }, [sessionId]);

    const handleUpload = async (file: File) => {
        if (!file.name.endsWith('.csv')) {
            alert("Please upload a CSV file.");
            return;
        }

        setLoading(true);
        setLoadingStep('📤 Uploading CSV...');
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://127.0.0.1:8000/upload', {
                method: 'POST',
                body: formData,
            });

            setLoadingStep('🧬 Profiling Data...');

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: "Unknown server error" }));
                throw new Error(errorData.detail || "Upload failed");
            }

            const data = await response.json();
            setSessionId(data.session_id);
            setProfile(data.profile);
            setPreview(data.preview);
            if (data.messages) setMessages(data.messages);
            if (data.suggested_prompts) setSuggestedPrompts(data.suggested_prompts);
        } catch (err: any) {
            console.error("Upload error:", err);
            alert(`Failed to upload dataset: ${err.message || "Ensure backend is running"}`);
        } finally {
            setLoading(false);
        }
    };

    const onDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
        else if (e.type === "dragleave") setDragActive(false);
    };

    const onDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleUpload(e.dataTransfer.files[0]);
        }
    };

    if (!mounted) return <div className="h-screen w-full bg-zinc-950" />;

    if (!sessionId) {
        return (
            <main className="h-screen w-full bg-zinc-950 flex items-center justify-center p-6 relative overflow-hidden">
                {/* Background Gradients */}
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-600/10 blur-[120px] rounded-full -translate-y-1/2 translate-x-1/2" />
                <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-teal-600/5 blur-[120px] rounded-full translate-y-1/2 -translate-x-1/2" />

                <div className="max-w-xl w-full text-center space-y-8 relative z-10">
                    <div className="space-y-4">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-xs font-medium text-blue-400 mb-2">
                            <ShieldAlert size={12} /> Secure Local Data Lab
                        </div>
                        <h1 className="text-6xl font-black tracking-tight bg-gradient-to-b from-white to-zinc-500 bg-clip-text text-transparent">
                            AI Data Lab
                        </h1>
                        <p className="text-zinc-400 text-lg">
                            Conversational Data Engineering & Engineering Studio.
                        </p>
                    </div>

                    <div
                        onDragEnter={onDrag}
                        onDragLeave={onDrag}
                        onDragOver={onDrag}
                        onDrop={onDrop}
                        className={`
              relative group p-12 border-2 border-dashed rounded-3xl transition-all duration-300
              ${dragActive ? 'border-blue-500 bg-blue-500/5 scale-105' : 'border-zinc-800 bg-zinc-900/40 hover:border-zinc-700'}
            `}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".csv"
                            className="hidden"
                            onChange={(e) => e.target.files && handleUpload(e.target.files[0])}
                        />

                        <div className="flex flex-col items-center gap-4">
                            <div className={`
                w-20 h-20 rounded-2xl flex items-center justify-center transition-all duration-500
                ${isLoading ? 'animate-pulse bg-blue-600/20' : 'bg-zinc-800 group-hover:bg-blue-600/10 group-hover:scale-110'}
              `}>
                                {isLoading ? (
                                    <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                                ) : (
                                    <Upload className="text-zinc-500 group-hover:text-blue-500 transition-colors" size={32} />
                                )}
                            </div>

                            <div className="space-y-1">
                                <p className="text-xl font-bold text-white">
                                    {isLoading ? (loadingStep || 'Analyzing Dataset...') : 'Drop CSV to Start'}
                                </p>
                                <p className="text-sm text-zinc-500">
                                    Import datasets up to 50MB. All processing is private.
                                </p>
                            </div>

                            {!isLoading && (
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    className="px-6 py-2 bg-white text-zinc-950 rounded-xl font-bold hover:bg-zinc-200 transition-colors mt-4"
                                >
                                    Select File
                                </button>
                            )}
                        </div>
                    </div>

                    <div className="flex items-center justify-center gap-8 pt-8 border-t border-zinc-900 text-zinc-600">
                        <div className="flex items-center gap-2 text-xs">
                            <CheckCircle size={14} className="text-emerald-500" /> Data Engineering
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                            <CheckCircle size={14} className="text-emerald-500" /> Analysis
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                            <CheckCircle size={14} className="text-emerald-500" /> Plotly Charts
                        </div>
                    </div>
                </div>
            </main>
        );
    }

    return (
        <main className="flex h-screen bg-zinc-950 overflow-hidden">
            <Sidebar />
            <div className="flex-1 flex overflow-hidden">
                <ChatArea />
                <DynamicPanel />
            </div>
        </main>
    );
}
