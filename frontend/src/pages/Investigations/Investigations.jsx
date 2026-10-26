import {useState} from 'react'
import {PageHeader,ResourceTable,InvestigationReview} from '../../components/ui/Shared'
import './Investigations.css'
export default function Investigations(){const [selected,setSelected]=useState(null),[version,setVersion]=useState(0);return <><PageHeader title="Investigations" description="Resolve exceptions with supporting records and explicit decisions."/><ResourceTable key={version} resource="investigations" columns={[["transaction_id","Payment"],["classification","Classification"],["status","Status"],["explanation","Evidence summary"]]} onSelect={setSelected}/>{selected&&<InvestigationReview row={selected} onSaved={()=>setVersion(v=>v+1)} onClose={()=>setSelected(null)}/>}</>}
