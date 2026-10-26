import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useData } from "../../hooks/useData";
import { post, formatMoney } from "../../services/api";
import {
  PageHeader,
  Notice,
  JsonView,
  Status,
} from "../../components/ui/Shared";
import { useAuth } from "../../context/Auth";
import "./InvoiceDetail.css";
export default function InvoiceDetail() {
  const { id } = useParams(),
    { user } = useAuth();
  const { data, error, loading, reload } = useData("/invoices/" + id);
  const [note, setNote] = useState(""),
    [failure, setFailure] = useState("");
  async function dispute(e) {
    e.preventDefault();
    try {
      await post(`/invoices/${id}/disputes`, { note });
      setNote("");
      reload();
    } catch (e) {
      setFailure(e.message);
    }
  }
  async function resolve(disputeId) {
    try {
      await post(`/disputes/${disputeId}/resolve`);
      reload();
    } catch (e) {
      setFailure(e.message);
    }
  }
  return (
    <>
      {loading ? (
        <p>Loading invoice…</p>
      ) : error ? (
        <Notice error>{error}</Notice>
      ) : (
        <>
          <PageHeader
            title={data.reference}
            description="Invoice evidence and immutable allocation history."
          >
            <Status value={data.status} />
          </PageHeader>
          <section className="panel">
            <dl className="detail-grid">
              {[
                ["Original amount", formatMoney(data.amount, data.currency)],
                ["Outstanding", formatMoney(data.outstanding, data.currency)],
                ["Due date", data.due_date],
                ["Issue date", data.issue_date],
              ].map(([key, value]) => (
                <div key={key}>
                  <dt>{key}</dt>
                  <dd>{value}</dd>
                </div>
              ))}
              <div>
                <dt>Customer</dt>
                <dd>
                  <Link to={"/customers/" + data.customer_id}>
                    View customer account
                  </Link>
                </dd>
              </div>
            </dl>
          </section>
          <section className="panel">
            <h2>Allocation history</h2>
            <JsonView value={data.allocations} />
          </section>
          <section className="panel">
            <h2>Disputes</h2>
            {data.disputes.map((d) => (
              <article key={d.id}>
                <p>
                  {d.note} · <Status value={d.status} />
                </p>
                {["admin", "reviewer"].includes(user.role) &&
                  d.status === "open" && (
                    <button className="secondary" onClick={() => resolve(d.id)}>
                      Resolve dispute
                    </button>
                  )}
              </article>
            ))}
            {failure && <Notice error>{failure}</Notice>}
            {user.role !== "viewer" && (
              <form onSubmit={dispute}>
                <label>
                  New dispute note
                  <textarea
                    required
                    minLength={5}
                    maxLength={2000}
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                  />
                </label>
                <button>Record dispute</button>
              </form>
            )}
          </section>
        </>
      )}
    </>
  );
}
