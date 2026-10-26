import {useParams} from 'react-router-dom'
import {useData} from '../../hooks/useData'
import {PageHeader,Notice,JsonView} from '../../components/ui/Shared'
import './CustomerDetail.css'
export default function CustomerDetail(){const {id}=useParams();const {data,error,loading}=useData('/customers/'+id);return <>{loading?<p>Loading account…</p>:error?<Notice error>{error}</Notice>:<><PageHeader title={data.name} description={`${data.account} · ${data.email}`}/><section className="panel"><h2>Invoices & balances</h2><JsonView value={data.invoices}/></section><section className="panel"><h2>Payments & reconciliation</h2><JsonView value={data.transactions}/></section></>}</>}
