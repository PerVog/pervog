import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Layers, ShieldCheck, Cpu, Code, Eye } from 'lucide-react';

export default function DebugAnalysis() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDebugData() {
      try {
        setLoading(true);
        const res = await fetch(`/api/ai/debug/analysis/${id || 'latest'}`);
        if (!res.ok) throw new Error(`Debug data error ${res.status}`);
        const json = await res.json();
        setData(json);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadDebugData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64 text-gray-400">
        <Layers className="animate-spin w-8 h-8 mr-2 text-indigo-400" /> Loading multi-model vision debug trace...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-900/40 border border-red-500/50 p-6 rounded-xl text-red-200">
        <h3 className="font-bold text-lg mb-2">Debug Analysis Error</h3>
        <p>{error || 'No debug analysis found for this ID.'}</p>
        <Link to="/" className="inline-flex items-center mt-4 text-indigo-400 hover:text-indigo-300">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to App
        </Link>
      </div>
    );
  }

  const { physical_regions = [], raw_detections = [], overall_outfit = {} } = data;

  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto text-gray-100">
      <div className="flex justify-between items-center border-b border-slate-700 pb-4">
        <div>
          <Link to="/" className="inline-flex items-center text-sm text-indigo-400 hover:text-indigo-300 mb-2">
            <ArrowLeft className="w-4 h-4 mr-1" /> Back to Stylist App
          </Link>
          <h1 className="text-3xl font-extrabold flex items-center gap-3">
            <Cpu className="text-indigo-400" /> Multi-Model Vision Pipeline Debugger
          </h1>
          <p className="text-gray-400 text-sm mt-1">Analysis ID: <span className="font-mono text-indigo-300">{data.analysis_id}</span></p>
        </div>
        <div className="bg-slate-800 border border-slate-700 px-4 py-2 rounded-lg text-right">
          <div className="text-xs text-gray-400 uppercase tracking-wider">Overall Outfit Style</div>
          <div className="text-lg font-bold text-emerald-400">{overall_outfit.style} (Formality: {overall_outfit.formality}/10)</div>
        </div>
      </div>

      {/* Visual Debug Image Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-3">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-indigo-300">
            <Eye className="w-5 h-5" /> Bounding Box Detections Visual
          </h2>
          <div className="bg-black rounded-lg overflow-hidden flex justify-center">
            <img src={data.detections_image} alt="Detections Visual" className="max-h-96 object-contain" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-3">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-indigo-300">
            <Layers className="w-5 h-5" /> Multi-Model Raw Detection Candidates ({raw_detections.length})
          </h2>
          <div className="bg-slate-950 p-3 rounded-lg max-h-96 overflow-y-auto font-mono text-xs text-slate-300 space-y-1">
            {raw_detections.map((det, i) => (
              <div key={i} className="flex justify-between border-b border-slate-800/80 py-1">
                <span className="text-indigo-400 font-bold">[{det.model}]</span>
                <span>{det.label}</span>
                <span className="text-emerald-400">{(det.score * 100).toFixed(0)}%</span>
                <span className="text-gray-500">[{det.box.join(', ')}]</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Physical Regions & Unique Crop Verification (PART 33) */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-100 flex items-center gap-2">
          <ShieldCheck className="text-emerald-400" /> Merged Physical Objects ({physical_regions.length})
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {physical_regions.map((reg, idx) => (
            <div key={reg.region_id || idx} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg flex flex-col">
              <div className="bg-slate-800/60 p-3 border-b border-slate-700/80 flex justify-between items-center">
                <span className="font-mono text-indigo-300 font-bold text-sm">{reg.region_id}</span>
                <span className="bg-indigo-900/60 text-indigo-300 text-xs px-2 py-0.5 rounded font-semibold uppercase">{reg.category}</span>
              </div>

              <div className="p-4 space-y-4 flex-1 flex flex-col justify-between">
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-black/80 rounded-lg p-2 flex flex-col items-center">
                    <span className="text-[10px] text-gray-400 uppercase mb-1">Item Crop</span>
                    {reg.image_url ? (
                      <img src={reg.image_url} alt={reg.display_name} className="h-32 object-contain" />
                    ) : (
                      <div className="h-32 flex items-center text-xs text-gray-500">No Crop Image</div>
                    )}
                  </div>

                  <div className="bg-black/80 rounded-lg p-2 flex flex-col items-center">
                    <span className="text-[10px] text-gray-400 uppercase mb-1">SAM Mask</span>
                    {reg.mask_url ? (
                      <img src={reg.mask_url} alt="Mask" className="h-32 object-contain bg-slate-900" />
                    ) : (
                      <div className="h-32 flex items-center text-xs text-gray-500">No Mask Image</div>
                    )}
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Predicted Type:</span>
                    <span className="font-bold text-white">{reg.display_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Mask Color:</span>
                    <span className="font-semibold text-indigo-300 capitalize">{reg.color?.primary}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Formality:</span>
                    <span className="font-semibold text-emerald-400">{reg.formality?.value}/10</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500">Crop SHA256:</span>
                    <span className="font-mono text-gray-400 truncate max-w-[120px]">{reg.crop_hash}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Raw Output JSON */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-3">
        <h2 className="text-lg font-semibold flex items-center gap-2 text-indigo-300">
          <Code className="w-5 h-5" /> Validated API JSON Response
        </h2>
        <pre className="bg-slate-950 p-4 rounded-lg overflow-x-auto font-mono text-xs text-emerald-400 max-h-96">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    </div>
  );
}
