import React from 'react';
import { Table as TableIcon, BarChart3, Maximize2, Download, BookOpen, Database } from 'lucide-react';
import { useDatasetStore } from '@/store/useDatasetStore';
import dynamic from 'next/dynamic';
import { DocumentationView } from '../docs/DocumentationView';

const Chart = dynamic(() => import('react-google-charts').then(mod => mod.Chart), {
    ssr: false,
    loading: () => <div className="h-full w-full flex items-center justify-center text-zinc-500">Loading Chart...</div>
}) as any;

export const DynamicPanel = () => {
    const { preview, activeChart, activeTab, setActiveTab } = useDatasetStore();

    // Automatically switch to chart tab when a new chart is generated
    React.useEffect(() => {
        if (activeChart) {
            setActiveTab('chart');
        }
    }, [activeChart, setActiveTab]);

    if (!preview && activeTab !== 'docs') return null;

    return (
        <div className="w-[450px] lg:w-[600px] h-full bg-zinc-950 border-l border-zinc-900 flex flex-col overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-zinc-900">
                <div className="flex bg-zinc-900 p-1 rounded-lg">
                    <button
                        onClick={() => setActiveTab('table')}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-all ${activeTab === 'table' ? 'bg-zinc-800 text-white shadow-sm' : 'text-zinc-500 hover:text-zinc-300'
                            }`}
                    >
                        <TableIcon size={14} /> Data
                    </button>
                    <button
                        onClick={() => setActiveTab('chart')}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-all ${activeTab === 'chart' ? 'bg-zinc-800 text-white shadow-sm' : 'text-zinc-500 hover:text-zinc-300'
                            }`}
                    >
                        <BarChart3 size={14} /> Insight
                    </button>
                    <button
                        onClick={() => setActiveTab('docs')}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-all ${activeTab === 'docs' ? 'bg-zinc-800 text-white shadow-sm' : 'text-zinc-500 hover:text-zinc-300'
                            }`}
                    >
                        <BookOpen size={14} /> Documentation
                    </button>
                </div>
                <div className="flex items-center gap-2">
                    <button className="p-2 text-zinc-500 hover:text-white hover:bg-zinc-900 rounded-lg transition-colors">
                        <Download size={16} />
                    </button>
                    <button className="p-2 text-zinc-500 hover:text-white hover:bg-zinc-900 rounded-lg transition-colors">
                        <Maximize2 size={16} />
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-auto p-4 custom-scrollbar">
                {activeTab === 'table' && preview ? (
                    <div className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-900/20">
                        <table className="w-full text-left text-xs border-collapse">
                            <thead>
                                <tr className="bg-zinc-900 text-zinc-400">
                                    {Object.keys(preview[0] || {}).map(key => (
                                        <th key={key} className="p-3 font-semibold border-b border-zinc-800 truncate max-w-[120px]">
                                            {key}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {preview.map((row, i) => (
                                    <tr key={i} className="border-b border-zinc-900 hover:bg-zinc-900/40 transition-colors">
                                        {Object.values(row).map((val: any, j) => (
                                            <th key={j} className="p-3 font-normal text-zinc-300 truncate max-w-[120px]">
                                                {String(val)}
                                            </th>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : activeTab === 'table' ? (
                    <div className="h-full flex flex-col items-center justify-center text-zinc-500">
                        <Database size={32} className="mb-4 opacity-20" />
                        <p>Upload a dataset to see the table</p>
                    </div>
                ) : activeTab === 'chart' ? (
                    <div className="h-full flex flex-col items-center justify-center">
                        {activeChart && activeChart.chartType && activeChart.data ? (
                            <div className="w-full h-full min-h-[400px]">
                                <Chart
                                    chartType={activeChart.chartType}
                                    data={activeChart.data}
                                    options={{
                                        ...(activeChart.options || {}),
                                        backgroundColor: 'transparent',
                                        legend: { textStyle: { color: '#a1a1aa' } },
                                        titleTextStyle: { color: '#e4e4e7' },
                                        hAxis: {
                                            ...(activeChart.options?.hAxis || {}),
                                            textStyle: { color: '#a1a1aa' },
                                            titleTextStyle: { color: '#a1a1aa' }
                                        },
                                        vAxis: {
                                            ...(activeChart.options?.vAxis || {}),
                                            textStyle: { color: '#a1a1aa' },
                                            titleTextStyle: { color: '#a1a1aa' }
                                        }
                                    }}
                                    width="100%"
                                    height="100%"
                                />
                            </div>
                        ) : (
                            <div className="text-center p-12">
                                <div className="w-16 h-16 bg-zinc-900 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-zinc-800">
                                    <BarChart3 size={32} className="text-zinc-700" />
                                </div>
                                <h3 className="text-zinc-300 font-medium mb-1">No visualizations yet</h3>
                                <p className="text-zinc-500 text-sm">Ask the agent to "Show trend" or "Visualize" your data.</p>
                            </div>
                        )}
                    </div>
                ) : (
                    <DocumentationView />
                )}
            </div>
        </div>
    );
};
