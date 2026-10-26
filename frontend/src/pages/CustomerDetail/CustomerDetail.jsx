import { useParams } from "react-router-dom";
import { useData } from "../../hooks/useData";
import { PageHeader, Notice, ResourceTable } from "../../components/ui/Shared";
import "./CustomerDetail.css";
export default function CustomerDetail() {
  const { id } = useParams();
  const { data, error, loading } = useData("/customers/" + id);
  const filter = "&customer_id=" + encodeURIComponent(id);
  return (
    <>
      {loading ? (
        <p>Loading account…</p>
      ) : error ? (
        <Notice error>{error}</Notice>
      ) : (
        <>
          <PageHeader
            title={data.name}
            description={`${data.account} · ${data.email}`}
          />
          <h2>Invoices & balances</h2>
          <ResourceTable
            resource="invoices"
            extra={filter}
            columns={[
              ["reference", "Invoice"],
              ["outstanding", "Outstanding"],
              ["currency", "Currency"],
              ["due_date", "Due date"],
              ["status", "Status"],
            ]}
          />
          <h2>Payments & reconciliation</h2>
          <ResourceTable
            resource="transactions"
            extra={filter}
            columns={[
              ["source_id", "Payment"],
              ["reference", "Reference"],
              ["amount", "Amount"],
              ["unallocated", "Unallocated"],
              ["status", "Status"],
            ]}
          />
          <h2>Disputes</h2>
          <ResourceTable
            resource="disputes"
            extra={filter}
            columns={[
              ["note", "Dispute note"],
              ["status", "Status"],
              ["created_at", "Recorded"],
            ]}
          />
          <h2>Communication history</h2>
          <ResourceTable
            resource="drafts"
            extra={filter}
            columns={[
              ["body", "Draft"],
              ["source", "Source"],
              ["status", "Status"],
              ["created_at", "Created"],
            ]}
          />
          <h2>Account timeline</h2>
          <ResourceTable
            resource="audit"
            extra={filter}
            columns={[
              ["created_at", "Timestamp"],
              ["action", "Action"],
              ["actor_id", "Actor"],
              ["record_id", "Record"],
            ]}
          />
        </>
      )}
    </>
  );
}
