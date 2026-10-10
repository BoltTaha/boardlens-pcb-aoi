import { useEffect, useMemo, useState } from 'react'
import { BarChart3, Boxes, ClipboardList, Cpu, Gauge, ScanLine, Settings, Upload } from 'lucide-react'
import { api, Inspection } from './api'

type View = 'inspect' | 'history' | 'analytics' | 'models' | 'configuration'
const nav: {id:View; label:string; icon:typeof ScanLine}[] = [
  {id:'inspect', label:'Inspection', icon:ScanLine}, {id:'history', label:'History', icon:ClipboardList},
  {id:'analytics', label:'Quality analytics', icon:BarChart3}, {id:'models', label:'Model performance', icon:Cpu},
  {id:'configuration', label:'Configuration', icon:Settings}
]

const Status = ({value}:{value:string}) => <span className={`status ${value.toLowerCase()}`}>{value}</span>

export function App() {
  const [view, setView] = useState<View>('inspect')
  const [history, setHistory] = useState<Inspection[]>([])
  const [selected, setSelected] = useState<Inspection | null>(null)
  const refresh = () => api.history().then(setHistory).catch(()=>setHistory([]))
  useEffect(() => { void refresh() }, [])
  return <div className="shell">
    <div className="topbar"><div className="brand"><div className="mark"><Boxes size={21}/></div><div><b>BoardLens</b><small>AOI CONTROL</small></div></div>
      <nav>{nav.map(item => <button className={view===item.id?'active':''} onClick={()=>setView(item.id)} key={item.id}><item.icon size={18}/>{item.label}</button>)}</nav>
    </div>
    <main><header className="page-header"><div><p className="eyebrow">MANUFACTURING VISION / LINE 01</p><h1>{nav.find(n=>n.id===view)?.label}</h1></div></header>
      {view==='inspect' && <Inspect onDone={(x)=>{setSelected(x);refresh()}} selected={selected}/>} 
      {view==='history' && <History rows={history} onSelect={(row)=>{setSelected(row);setView('inspect')}}/>} 
      {view==='analytics' && <Analytics rows={history}/>} 
      {view==='models' && <Models/>} 
      {view==='configuration' && <Configuration/>}
    </main>
  </div>
}

function Inspect({onDone, selected}:{onDone:(x:Inspection)=>void;selected:Inspection|null}) {
  const [product,setProduct]=useState('pcb1'); const [file,setFile]=useState<File|null>(null); const [busy,setBusy]=useState(false); const [error,setError]=useState('')
  const [layer,setLayer]=useState<'overlay'|'original'>('overlay')
  const preview=useMemo(()=>file?URL.createObjectURL(file):null,[file])
  const run=async()=>{if(!file)return;setBusy(true);setError('');try{onDone(await api.inspect(product,file))}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
  return <section className="grid inspection-grid"><div className="panel controls"><div className="panel-title"><div><p className="eyebrow">CAPTURE</p><h2>New inspection</h2></div><Gauge size={20}/></div>
    <label>PCB product<select value={product} onChange={e=>setProduct(e.target.value)}><option value="pcb1">VisA PCB1</option><option value="pcb2">VisA PCB2</option><option value="pcb3">VisA PCB3</option><option value="pcb4">VisA PCB4</option></select></label>
    <label className="drop"><Upload size={28}/><b>{file?file.name:'Select inspection image'}</b><small>JPEG, PNG or WebP · max 15 MB</small><input type="file" accept="image/png,image/jpeg,image/webp" onChange={e=>setFile(e.target.files?.[0]??null)}/></label>
    <button className="primary" disabled={!file||busy} onClick={run}>{busy?'Inspecting…':'Run inspection'}</button>{error&&<p className="error">{error}</p>}
    <div className="notice">A missing or uncalibrated model yields REVIEW. BoardLens does not synthesize predictions.</div></div>
    <div className="panel viewer"><div className="panel-title"><div><p className="eyebrow">VISUAL EVIDENCE</p><h2>Inspection frame</h2></div><div className="viewer-tools">{selected&&<div className="segments"><button className={layer==='original'?'active':''} onClick={()=>setLayer('original')}>Original</button><button className={layer==='overlay'?'active':''} onClick={()=>setLayer('overlay')}>Anomaly map</button></div>}{selected&&<Status value={selected.decision}/>}</div></div>
      <div className="image-stage">{(selected?.image_url||preview)?<img src={selected?(layer==='overlay'?(selected.overlay_url||selected.image_url):selected.image_url):preview!}/>:<div><ScanLine size={50}/><p>No frame selected</p></div>}</div>
      {selected&&<div className="result"><div><small>Decision</small><strong>{selected.decision}</strong></div><div><small>Anomaly score</small><strong>{selected.anomaly_score?.toFixed(3)??'Unavailable'}</strong></div><div><small>Latency</small><strong>{selected.latency_ms.toFixed(1)} ms</strong></div><div><small>Model</small><strong>{selected.model_id}</strong></div><p>{selected.reasons.join(' ')}</p></div>}
    </div></section>
}

function History({rows,onSelect}:{rows:Inspection[];onSelect:(x:Inspection)=>void}) { return <section className="panel"><div className="panel-title"><div><p className="eyebrow">AUDIT TRAIL</p><h2>Recorded inspections</h2></div><span>{rows.length} records</span></div><div className="table"><div className="tr head"><span>ID</span><span>Product</span><span>Decision</span><span>Model</span><span>Latency</span><span>Timestamp</span></div>{rows.map(r=><button className="tr" onClick={()=>onSelect(r)} key={r.id}><span className="mono">{r.id.slice(0,8)}</span><span>{r.product.toUpperCase()}</span><span><Status value={r.decision}/></span><span>{r.model_id}</span><span>{r.latency_ms.toFixed(1)} ms</span><span>{new Date(r.created_at).toLocaleString()}</span></button>)}</div>{!rows.length&&<div className="empty">No inspections recorded yet.</div>}</section> }

function Analytics({rows}:{rows:Inspection[]}) { const count=(d:string)=>rows.filter(r=>r.decision===d).length; const pct=(n:number)=>rows.length?`${(100*n/rows.length).toFixed(1)}%`:'—'; return <><section className="cards"><Metric label="Total inspected" value={String(rows.length)}/><Metric label="Predicted pass rate" value={pct(count('PASS'))}/><Metric label="Predicted fail rate" value={pct(count('FAIL'))}/><Metric label="Review rate" value={pct(count('REVIEW'))}/></section><section className="panel"><div className="panel-title"><div><p className="eyebrow">GOVERNANCE NOTE</p><h2>Interpretation</h2></div></div><p className="copy">These are model decisions for recorded inspections, not a verified factory defect rate. Ground-truth disposition and operator overrides must be analyzed separately.</p></section></> }
function Metric({label,value}:{label:string;value:string}){return <div className="metric"><small>{label}</small><strong>{value}</strong><span>Recorded API data</span></div>}
function Models(){const [models,setModels]=useState<Record<string,any>>({});useEffect(()=>{api.models().then(x=>setModels((x as any).models??{})).catch(()=>setModels({}))},[]);return <section className="panel"><div className="panel-title"><div><p className="eyebrow">MODEL REGISTRY</p><h2>Evaluation status</h2></div></div>{Object.entries(models).map(([id,value])=><div className="model-row" key={id}><div><b>{id}</b><p>{value.algorithm??value.framework} · {value.product??value.task}{value.evaluation_metrics?` · image AUROC ${value.evaluation_metrics.heldout_image_auroc}`:''}</p><p>{value.limitations}</p></div><Status value={String(value.status).toUpperCase()}/></div>)}</section>}
function Configuration(){return <section className="panel"><div className="panel-title"><div><p className="eyebrow">RECIPE CONTROL</p><h2>Threshold governance</h2></div></div><p className="copy">Product recipes are versioned in <code>configs/products.yaml</code>. PCB1 uses a validation-selected proof-of-concept threshold with a documented high false-positive rate; PCB2–PCB4 remain uncalibrated and unavailable.</p></section>}
