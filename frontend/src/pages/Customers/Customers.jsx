import {PageHeader,ResourceTable} from '../../components/ui/Shared'
import './Customers.css'
export default function Customers(){return <><PageHeader title="Customers" description="Account context for informed financial decisions."/><ResourceTable resource="customers" columns={[["name","Customer"],["account","Account"],["email","Contact"]]}/></>}
