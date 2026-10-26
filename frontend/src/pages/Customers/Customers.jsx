import { useState } from "react";
import {
  PageHeader,
  ResourceTable,
  Modal,
  Notice,
} from "../../components/ui/Shared";
import { useAuth } from "../../context/Auth";
import { post } from "../../services/api";
import "./Customers.css";
export default function Customers() {
  const { user } = useAuth(),
    [open, setOpen] = useState(false),
    [name, setName] = useState(""),
    [account, setAccount] = useState(""),
    [email, setEmail] = useState(""),
    [error, setError] = useState("");
  async function save(e) {
    e.preventDefault();
    try {
      await post("/customers", { name, account, email });
      setOpen(false);
      setName("");
      setAccount("");
      setEmail("");
    } catch (e) {
      setError(e.message);
    }
  }
  return (
    <>
      <PageHeader
        title="Customers"
        description="Account context for informed financial decisions."
      >
        {user.role !== "viewer" && (
          <button onClick={() => setOpen(true)}>Add customer</button>
        )}
      </PageHeader>
      <ResourceTable
        key={String(open)}
        resource="customers"
        columns={[
          ["name", "Customer"],
          ["account", "Account"],
          ["email", "Contact"],
        ]}
      />
      {open && (
        <Modal title="Add customer" onClose={() => setOpen(false)}>
          <form onSubmit={save}>
            <label>
              Customer name
              <input
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </label>
            <label>
              Account reference
              <input
                required
                pattern="[A-Za-z0-9_-]+"
                value={account}
                onChange={(e) => setAccount(e.target.value)}
              />
            </label>
            <label>
              Contact email
              <input
                required
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>
            {error && <Notice error>{error}</Notice>}
            <button>Save customer</button>
          </form>
        </Modal>
      )}
    </>
  );
}
