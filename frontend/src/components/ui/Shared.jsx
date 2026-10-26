import {useEffect,useRef,useState} from 'react'
import {Link} from 'react-router-dom'
import {Search,ChevronLeft,ChevronRight,X} from 'lucide-react'
import {useData} from '../../hooks/useData'
import {api,formatMoney,post} from '../../services/api'
import {useAuth} from '../../context/Auth'
export function Status({value}){return <span className={`status ${['failed','disputed','rejected','duplicate','reversal'].includes(value)?'attention':''}`}>{String(value || '—').replaceAll('_',' ')}</span>}
export function PageHeader({eyebrow='Finance operations',title,description,children}){return <header className="page-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="muted">{description}</p></div><div className="actions">{children}</div></header>}
export function Notice({error,children}){return <div className={error?'notice error':'notice'} role={error?'alert':'status'}>{children}</div>}
export function JsonView({value}){return <pre className="json-view">{JSON.stringify(value,null,2)}</pre>}
export function Modal({title,children,onClose}){
 const ref=useRef(null)
 useEffect(()=>{const dialog=ref.current;dialog.showModal();return()=>dialog.close()},[])
 return <dialog ref={ref} onCancel={onClose}><div className="modal-heading"><h2>{title}</h2><button className="icon-button" aria-label="Close" onClick={onClose}><X size={20}/></button></div>{children}</dialog>
}
function Cell({value,column,row}){
 if(column==='status')return <Status value={value}/>
 if(['amount','outstanding','unallocated'].includes(column))return <span className="money">{formatMoney(value,row.currency)}</span>
 if(['proposal','detail','summary','result','checkpoint','usage'].includes(column))return <span className="muted">{Object.keys(value || {}).length} fields</span>
 if(column==='reference' && row.due_date)return <Link to={`/invoices/${row.id}`}>{value}</Link>
 if(column==='name')return <Link to={`/customers/${row.id}`}>{value}</Link>
 if(column==='created_at')return <time>{new Date(value).toLocaleString('en-ZA',{dateStyle:'medium',timeStyle:'short'})}</time>
 return <span title={typeof value==='object'?JSON.stringify(value):String(value ?? '')}>{typeof value==='boolean'?(value?'Yes':'No'):typeof value==='object'?JSON.stringify(value):String(value ?? '—')}</span>
}
export function ResourceTable({resource,columns,actions,onSelect,extra=''}){
 const [q,setQ]=useState(''),[status,setStatus]=useState(''),[page,setPage]=useState(1),[sort,setSort]=useState(''),[direction,setDirection]=useState('asc')
 const path=`/${resource}?q=${encodeURIComponent(q)}&status=${status}&page=${page}&sort=${sort}&direction=${direction}${extra}`
 const {data,error,loading,reload}=useData(path)
 return <section className="panel"><div className="table-toolbar"><label className="search"><Search size={17}/><input aria-label={`Search ${resource}`} placeholder={`Search ${resource.replaceAll('-',' ')}…`} value={q} onChange={e=>{setQ(e.target.value);setPage(1)}}/></label><label className="filter-label">Status<select aria-label="Filter status" value={status} onChange={e=>{setStatus(e.target.value);setPage(1)}}><option value="">All statuses</option>{['open','overdue','paid','unallocated','allocated','human_review','needs_information','rejected','queued','running','completed','failed','not_executed','draft','approved_not_sent','preview','confirmed'].map(s=><option key={s} value={s}>{s.replaceAll('_',' ')}</option>)}</select></label><button className="secondary" onClick={reload}>Refresh</button></div>
 {error?<Notice error>{error}</Notice>:loading?<p className="empty" role="status">Loading records…</p>:<><div className="table-scroll"><table><thead><tr>{columns.map(([key,label])=><th key={key}><button className="sort" onClick={()=>{setSort(key);setDirection(direction==='asc'?'desc':'asc')}}>{label}{sort===key?(direction==='asc'?' ↑':' ↓'):''}</button></th>)}{(actions||onSelect)&&<th>Review</th>}</tr></thead><tbody>{data?.items.map(row=><tr key={row.id}>{columns.map(([key])=><td key={key}><Cell value={row[key]} column={key} row={row}/></td>)}{(actions||onSelect)&&<td>{actions?.(row,reload)}{onSelect&&<button className="text-button" onClick={()=>onSelect(row,reload)}>View details</button>}</td>}</tr>)}</tbody></table></div>{!data?.items.length&&<p className="empty">No records match this view.</p>}<footer className="pagination"><span>{data?.total || 0} records · Page {page}</span><div><button aria-label="Previous page" disabled={page===1} onClick={()=>setPage(p=>p-1)}><ChevronLeft size={16}/></button><button aria-label="Next page" disabled={page*25>=(data?.total||0)} onClick={()=>setPage(p=>p+1)}><ChevronRight size={16}/></button></div></footer></>}
 </section>
}
export function ImportDialog({kind,onClose}){
 const [file,setFile]=useState(null),[mapping,setMapping]=useState('{}'),[preview,setPreview]=useState(null),[error,setError]=useState(''),[busy,setBusy]=useState(false)
 async function submit(e){e.preventDefault();setBusy(true);setError('');try{const form=new FormData();form.append('file',file);form.append('mapping',mapping);setPreview(await post(`/imports/${kind}/preview`,form))}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function confirm(){setBusy(true);try{setPreview(await post(`/imports/${preview.id}/confirm`))}catch(e){setError(e.message)}finally{setBusy(false)}}
 return <Modal title={`Import ${kind}`} onClose={onClose}><p>UTF-8 CSV, up to 2 MB and 5,000 rows. Validate every row before confirming.</p><p className="muted">{kind==='invoices'?'reference, account, amount, currency, issue_date, due_date':'source_id, account, reference, amount, currency, payment_date'}</p><form onSubmit={submit}><label>CSV file<input required type="file" accept=".csv,text/csv" onChange={e=>{setFile(e.target.files[0]);setPreview(null)}}/></label><label>Column mapping (canonical name → your column)<textarea value={mapping} onChange={e=>setMapping(e.target.value)}/></label><button disabled={busy||!file}>Validate preview</button></form>{error&&<Notice error>{error}</Notice>}{preview&&<><h3>Validation preview</h3><p>{preview.rows.length} valid rows · {preview.errors.length} errors · <Status value={preview.status}/></p><JsonView value={preview.errors.length?preview.errors:preview.rows.slice(0,5)}/><button disabled={busy||preview.errors.length>0||preview.status==='confirmed'} onClick={confirm}>Confirm import</button></>}</Modal>
}
export function DetailDialog({resource,row,onClose}){
 const {data,error,loading}=useData(`/${resource}/${row.id}`)
 return <Modal title="Record details" onClose={onClose}>{loading?<p>Loading…</p>:error?<Notice error>{error}</Notice>:<JsonView value={data}/>}</Modal>
}
export function InvestigationReview({row,onClose,onSaved}){
 const {user}=useAuth(),[caseData,setCaseData]=useState(row),[note,setNote]=useState(''),[manual,setManual]=useState(JSON.stringify(row.proposal?.allocations || [],null,2)),[error,setError]=useState(''),[busy,setBusy]=useState(false)
 const canReview=['admin','reviewer'].includes(user.role)
 async function decide(decision){setBusy(true);setError('');try{await post(`/investigations/${row.id}/review`,{decision,note,allocations:decision==='approve'?JSON.parse(manual):null},{'Idempotency-Key':crypto.randomUUID()});onSaved();onClose()}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function run(){setBusy(true);try{const result=await post(`/investigations/${row.id}/run`);setCaseData({...caseData,execution:result});onSaved()}catch(e){setError(e.message)}finally{setBusy(false)}}
 return <Modal title="Investigation review" onClose={onClose}><p><Status value={caseData.status}/> <span className="muted">{row.classification.replaceAll('_',' ')}</span></p><p>{row.explanation}</p><JsonView value={caseData.proposal}/><button className="secondary" disabled={busy||user.role==='viewer'} onClick={run}>Request CrewAI investigation</button>{caseData.execution&&<JsonView value={caseData.execution}/>}<hr/><label>Proposed allocations (invoice ID and decimal amount)<textarea rows={6} value={manual} onChange={e=>setManual(e.target.value)} disabled={!canReview}/></label><label>Review note<textarea value={note} onChange={e=>setNote(e.target.value)} placeholder="Explain your decision"/></label><p className="muted">Approval revalidates the customer, currency, disputes and available balances. Communications remain disabled.</p>{error&&<Notice error>{error}</Notice>}<div className="actions"><button disabled={busy||!canReview||note.length<3||row.status==='allocated'} onClick={()=>decide('approve')}>Approve allocation</button><button className="secondary" disabled={busy||!canReview||note.length<3} onClick={()=>decide('reject')}>Reject</button><button className="text-button" disabled={busy||!canReview||note.length<3} onClick={()=>decide('request_information')}>Request information</button></div></Modal>
}
