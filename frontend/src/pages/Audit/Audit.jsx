import {useState} from 'react'
import {PageHeader,ResourceTable,DetailDialog} from '../../components/ui/Shared'
import './Audit.css'
export default function Audit(){const [selected,setSelected]=useState(null);return <><PageHeader title="Audit trail" description="Every material decision, its actor and its supporting context."/><ResourceTable resource="audit" columns={[["created_at","Timestamp"],["action","Action"],["actor_id","Actor"],["record_id","Affected record"],["correlation_id","Correlation ID"]]} onSelect={setSelected}/>{selected&&<DetailDialog resource="audit" row={selected} onClose={()=>setSelected(null)}/>}</>}
