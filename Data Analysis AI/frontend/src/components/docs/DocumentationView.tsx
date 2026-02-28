import React from 'react';
import { Book, Code, Layers, Layout, Target, Zap, CheckCircle, Info } from 'lucide-react';

export const DocumentationView = () => {
    return (
        <div className="flex-1 overflow-y-auto p-8 bg-zinc-950 text-zinc-300 custom-scrollbar pb-32">
            <div className="max-w-4xl mx-auto space-y-12">
                {/* Header */}
                <header className="border-b border-zinc-900 pb-8">
                    <h1 className="text-4xl font-bold text-white mb-4">AI Data Lab: Advanced Analytics Engine</h1>
                    <p className="text-zinc-500 text-lg">Comprehensive Project Documentation & Research Report</p>
                </header>

                {/* Milestones / Reviews */}
                <section className="space-y-6">
                    <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
                        <Target className="text-blue-500" size={24} /> Project Milestones
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-zinc-900/50 p-6 rounded-2xl border border-zinc-900">
                            <h3 className="text-blue-400 font-bold mb-2">0th Review (15-12-2025)</h3>
                            <ul className="text-sm space-y-1 text-zinc-500">
                                <li>• Title: AI-Powered Autonomous Data Scientist</li>
                                <li>• Objective: Eliminate manual data cleaning</li>
                                <li>• Stack: Python/React Foundation</li>
                            </ul>
                        </div>
                        <div className="bg-zinc-900/50 p-6 rounded-2xl border border-zinc-900">
                            <h3 className="text-teal-400 font-bold mb-2">1st Review (29-12-2025)</h3>
                            <ul className="text-sm space-y-1 text-zinc-500">
                                <li>• Problem: Static analysis tools lack reasoning</li>
                                <li>• Data Flow: Raw CSV → LLM Transform → Visuals</li>
                                <li>• Logic: Multi-Agent Router Architecture</li>
                            </ul>
                        </div>
                    </div>
                </section>

                {/* Chapter 1: Introduction */}
                <section className="space-y-4">
                    <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
                        <Info className="text-purple-500" size={24} /> Chapter 1 - Introduction
                    </h2>
                    <div className="prose prose-invert max-w-none">
                        <p>
                            In the modern era of Big Data, the bottleneck for most organizations is not the lack of data, but the lack of
                            <strong> actionable insights</strong>. Professional data scientists spend over 80% of their time on "data wrangling"—cleaning,
                            normalizing, and transforming raw datasets before any analysis can begin.
                        </p>
                        <p>
                            <strong>AI Data Lab</strong> is an intelligent agentic system designed to bridge this gap. By leveraging Large Language Models (LLMs)
                            distributed across cloud (OpenAI/Gemini) and local (DeepSeek/Ollama) environments, the project provides a conversational interface
                            that understands raw data files, automates complex engineering tasks, and generates professional visualizations instantaneously.
                        </p>
                    </div>
                </section>

                {/* Architecture Diagram */}
                <section className="space-y-4">
                    <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
                        <Layers className="text-orange-500" size={24} /> System Architecture
                    </h2>
                    <div className="bg-zinc-900 p-8 rounded-2xl border border-zinc-800 font-mono text-xs overflow-x-auto">
                        <pre className="text-zinc-400">
                            {`graph TD
    A[User Interface - Next.js] -->|Chat/Upload| B[FastAPI Gateway]
    B --> C{Agent Router}
    C -->|Analysis| D[Analyst Agent]
    C -->|Engineering| E[Engineer Agent]
    C -->|Visuals| F[Visualization Agent]
    
    D & E & F -->|Routing| G{LLM Bridge}
    G -->|Cloud| H[OpenAI / Gemini]
    G -->|Local| I[Ollama / DeepSeek-R1]
    
    B --> J[Session Persistence - JSON/Parquet]
    J --> K[Local Storage]`}
                        </pre>
                        <p className="mt-4 text-[10px] text-zinc-600 italic uppercase tracking-widest text-center">Mermaid Architecture Flow</p>
                    </div>
                </section>

                {/* Chapter 2: System Design */}
                <section className="space-y-4">
                    <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
                        <Layout className="text-green-500" size={24} /> Chapter 2 - System Design
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="space-y-2">
                            <h4 className="text-white font-bold flex items-center gap-2"><Zap size={16} /> Data Pre-processing</h4>
                            <p className="text-sm text-zinc-500">Automated type inference and missing value detection using Pandas profiling.</p>
                        </div>
                        <div className="space-y-2">
                            <h4 className="text-white font-bold flex items-center gap-2"><Code size={16} /> Multi-LLM Routing</h4>
                            <p className="text-sm text-zinc-500">Dynamic switching between OpenAI (accuracy) and local DeepSeek (privacy/zero-cost).</p>
                        </div>
                        <div className="space-y-2">
                            <h4 className="text-white font-bold flex items-center gap-2"><CheckCircle size={16} /> Visualization</h4>
                            <p className="text-sm text-zinc-500">Google Charts integration for interactive, responsive data representation.</p>
                        </div>
                    </div>
                </section>

                {/* Chapter 3: Software Design */}
                <section className="space-y-6 bg-zinc-900/40 p-8 rounded-3xl border border-zinc-900">
                    <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
                        <Layers className="text-blue-400" size={24} /> Chapter 3 - Software Design
                    </h2>
                    <div className="space-y-8">
                        <div>
                            <h3 className="text-white font-bold mb-3 border-l-2 border-blue-500 pl-4 uppercase text-xs tracking-widest">Front End Layer</h3>
                            <ul className="space-y-2 text-sm text-zinc-500">
                                <li><strong className="text-zinc-300">Next.js 15:</strong> Core framework for SSR and App Routing.</li>
                                <li><strong className="text-zinc-300">Tailwind CSS:</strong> For the futuristic, dark-mode "Glassmorphism" UI.</li>
                                <li><strong className="text-zinc-300">Zustand:</strong> Efficient global state management for chat and dataset streams.</li>
                                <li><strong className="text-zinc-300">Lucide React:</strong> Premium iconography for enhanced UX.</li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="text-white font-bold mb-3 border-l-2 border-green-500 pl-4 uppercase text-xs tracking-widest">Back End Layer</h3>
                            <ul className="space-y-2 text-sm text-zinc-500">
                                <li><strong className="text-zinc-300">FastAPI:</strong> High-performance asynchronous REST implementation.</li>
                                <li><strong className="text-zinc-300">Python Pandas:</strong> Industrial-grade data manipulation and math.</li>
                                <li><strong className="text-zinc-300">Ollama SDK:</strong> Local LLM orchestration for DeepSeek-R1.</li>
                                <li><strong className="text-zinc-300">Google GenAI:</strong> Native integration with Gemini 1.5 Pro.</li>
                            </ul>
                        </div>
                    </div>
                </section>

                {/* Chapter 4: Results & Conclusion */}
                <section className="space-y-4">
                    <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
                        <CheckCircle className="text-teal-500" size={24} /> Chapter 4 & 5 - Results & Conclusion
                    </h2>
                    <p className="prose prose-invert text-zinc-400">
                        The final implementation successfully demonstrates <strong>Zero-Configuration Data Science</strong>.
                        Users can upload any CSV/Parquet file and receive instant exploratory data analysis (EDA). The
                        integration of the <strong>AbortController</strong> ensures local model latency doesn't break the user experience,
                        providing a robust, enterprise-grade interface.
                    </p>
                    <div className="flex bg-blue-600/10 border border-blue-600/20 p-6 rounded-2xl items-start gap-4">
                        <Zap className="text-blue-500 mt-1" size={20} />
                        <div>
                            <h4 className="text-blue-400 font-bold mb-1">Final Summary</h4>
                            <p className="text-xs text-zinc-500 leading-relaxed">
                                AI Data Lab proves that specialized LLM agents can handle the "heavy lifting" of data engineering,
                                allowing humans to focus on decision-making rather than syntax.
                            </p>
                        </div>
                    </div>
                </section>

                {/* References */}
                <section className="pt-8 border-t border-zinc-900">
                    <h3 className="text-lg font-bold text-white mb-4">References</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono text-zinc-600">
                        <p>1. "Agentic Workflows in LLMs" - ML Review 2024</p>
                        <p>2. FastAPI Documentation (fastapi.tiangolo.com)</p>
                        <p>3. Ollama Open Source Repository (ollama.com)</p>
                        <p>4. Next.js Patterns - Vercel Documentation</p>
                    </div>
                </section>
            </div>
        </div>
    );
};
