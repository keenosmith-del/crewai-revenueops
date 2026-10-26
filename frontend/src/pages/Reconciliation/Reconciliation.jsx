import { useState } from "react";
import {
  PageHeader,
  ResourceTable,
  Notice,
  InvestigationReview,
  DetailDialog,
} from "../../components/ui/Shared";
import { post } from "../../services/api";
import { useAuth } from "../../context/Auth";
import "./Reconciliation.css";
export default function Reconciliation() {
  const [version, setVersion] = useState(0),
    [selected, setSelected] = useState(null),
    [batch, setBatch] = useState(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const { user } = useAuth();
  async function run() {
    setBusy(true);
    setError("");
    try {
      await post("/reconciliation");
      setVersion((v) => v + 1);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeader
        title="Reconciliation"
        description="Deterministic matching first. Human judgment at every allocation."
      >
        <button disabled={busy || user.role === "viewer"} onClick={run}>
          {busy ? "Matching records…" : "Run reconciliation"}
        </button>
      </PageHeader>
      {error && <Notice error>{error}</Notice>}
      <ResourceTable
        key={version}
        resource="investigations"
        columns={[
          ["transaction_id", "Payment"],
          ["classification", "Match classification"],
          ["status", "Status"],
          ["explanation", "Finding"],
        ]}
        onSelect={setSelected}
      />
      <h2>Batch history</h2>
      <ResourceTable
        key={"batch" + version}
        resource="batches"
        onSelect={setBatch}
        columns={[
          ["created_at", "Created"],
          ["status", "Status"],
          ["summary", "Classification results"],
        ]}
      />
      {batch && (
        <DetailDialog
          resource="batches"
          row={batch}
          onClose={() => setBatch(null)}
        />
      )}
      {selected && (
        <InvestigationReview
          row={selected}
          onSaved={() => setVersion((v) => v + 1)}
          onClose={() => setSelected(null)}
        />
      )}
    </>
  );
}
