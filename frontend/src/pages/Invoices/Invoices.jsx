import {useState} from 'react'
import {PageHeader,ResourceTable,ImportDialog} from '../../components/ui/Shared'
import {useAuth} from '../../context/Auth'
import './Invoices.css'
export default function Invoices(){const [open,setOpen]=useState(false);const {user}=useAuth();return <><PageHeader title="Invoices" description="Every invoice, its balance and the evidence behind it.">{user.role!=='viewer'&&<button onClick={()=>setOpen(true)}>Import invoices</button>}</PageHeader><ResourceTable key={String(open)} resource="invoices" columns={[["reference","Invoice"],["amount","Original amount"],["outstanding","Outstanding"],["currency","Currency"],["due_date","Due date"],["status","Status"]]}/>{open&&<ImportDialog kind="invoices" onClose={()=>setOpen(false)}/>}</>}
