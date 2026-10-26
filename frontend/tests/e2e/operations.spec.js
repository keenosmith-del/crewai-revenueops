import { test, expect } from "@playwright/test";
async function signIn(page) {
  // Financial write tests are permitted only against an isolated synthetic test service.

  await page.goto("/");
  await page
    .getByLabel("Email", { exact: true })
    .fill("reviewer@revenueops.example");
  await page.getByLabel("Password", { exact: true }).fill("Demo-finance-2026!");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "A clearer view of your receivables." }),
  ).toBeVisible();
  const identity = await (await page.request.get("/api/auth/me")).json();
  const configuration = await (await page.request.get("/api/settings")).json();
  expect(identity.synthetic).toBe(true);
  expect(configuration.environment).toBe("test");
}
test("reconcile, approve, persist and audit", async ({ page }) => {
  await signIn(page);
  await page.getByRole("link", { name: "Reconciliation", exact: true }).click();
  await page
    .getByRole("button", { name: "Run reconciliation", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "View details" }).first(),
  ).toBeVisible();
  const cases = await page.request.get("/api/investigations?page_size=200");
  const items = (await cases.json()).items;
  const candidate = items.find(
    (i) => i.classification === "exact" && i.status === "human_review",
  );
  if (candidate) {
    await page
      .getByLabel("Search investigations")
      .fill(candidate.transaction_id);
    const target = page.getByRole("row").filter({
      has: page.getByText(candidate.transaction_id, { exact: true }),
    });
    await target.getByRole("button", { name: "View details" }).click();
    await page
      .getByLabel("Review note")
      .fill("Verified synthetic receipt and invoice evidence");
    await page
      .getByRole("button", { name: "Approve allocation", exact: true })
      .click();
    await expect(page.getByRole("dialog")).not.toBeVisible();
    await page.reload();
    const persisted = await page.request.get(
      "/api/investigations/" + candidate.id,
    );
    expect((await persisted.json()).status).toBe("allocated");
  }

  await page.getByRole("link", { name: "Audit trail", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Audit trail" }),
  ).toBeVisible();
  await expect(
    page.getByText("reconciliation.completed", { exact: true }).first(),
  ).toBeVisible();
  await page.goto("/");
  await expect(page.getByText("Loading financial overview…")).not.toBeVisible();
  await page.screenshot({
    path: "test-results/desktop-dashboard.png",
    fullPage: true,
  });
});
test("import validation and collection approval never sends", async ({
  page,
}) => {
  await signIn(page);
  await page.getByRole("link", { name: "Invoices", exact: true }).click();
  await page.getByRole("button", { name: "Import invoices" }).click();
  await page.getByLabel("CSV file").setInputFiles({
    name: "browser.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(
      "reference,account,amount,currency,issue_date,due_date\nBROWSER-" +
        Date.now() +
        ",SYN-000,45.00,ZAR,2026-01-01,2026-02-01\n",
    ),
  });
  await page.getByRole("button", { name: "Validate preview" }).click();
  await expect(page.getByText("1 valid rows", { exact: false })).toBeVisible();
  await page
    .getByRole("button", { name: "Confirm import", exact: true })
    .click();
  await expect(
    page
      .getByRole("dialog")
      .locator(".status")
      .filter({ hasText: /^confirmed$/ }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Close", exact: true }).click();
  await page.getByRole("link", { name: "Collections", exact: true }).click();
  await page.getByRole("button", { name: "Prepare draft" }).first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page
    .getByRole("button", { name: "Approve draft", exact: true })
    .click();
  await expect(
    page
      .getByRole("dialog")
      .locator(".status")
      .filter({ hasText: /^approved not sent$/ }),
  ).toBeVisible();
});
test("responsive navigation and settings", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 390, height: 844 });
  await signIn(page);
  await page.getByRole("button", { name: "Toggle navigation" }).click();
  await page.getByRole("link", { name: "Settings", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Settings", exact: true }),
  ).toBeVisible();
  await expect(page.locator(".sidebar")).toHaveCSS("transform", "matrix(1, 0, 0, 1, -244, 0)");
  await expect(page.getByText("baseline", { exact: true })).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: "test-results/mobile-settings.png",
    fullPage: true,
  });
});

test("import both ledgers, disclose baseline, approve and verify isolated fixture balance", async ({
  page,
}) => {
  await signIn(page);
  const stamp = Date.now();
  const invoiceReference = `E2E-INV-${stamp}`;
  const paymentReference = `E2E-PAY-${stamp}`;
  async function upload(kind, content) {
    await page.goto("/" + kind);
    await page
      .getByRole("button", { name: "Import " + kind, exact: true })
      .click();
    await page
      .getByLabel("CSV file")
      .setInputFiles({
        name: "synthetic.csv",
        mimeType: "text/csv",
        buffer: Buffer.from(content),
      });
    await page.getByRole("button", { name: "Validate preview" }).click();
    await expect(
      page.getByText("1 valid rows", { exact: false }),
    ).toBeVisible();
    await page
      .getByRole("button", { name: "Confirm import", exact: true })
      .click();
    await expect(page.getByRole("dialog").locator(".status")).toHaveText(
      "confirmed",
    );
    await page.getByRole("button", { name: "Close", exact: true }).click();
  }
  await upload(
    "invoices",
    `reference,account,amount,currency,issue_date,due_date\n${invoiceReference},SYN-000,17.35,ZAR,2026-01-01,2026-02-01\n`,
  );
  await upload(
    "transactions",
    `source_id,account,reference,amount,currency,payment_date\n${paymentReference},SYN-000,${invoiceReference},17.35,ZAR,2026-02-02\n`,
  );
  const payment = (
    await (
      await page.request.get("/api/transactions?q=" + paymentReference)
    ).json()
  ).items[0];
  await page.goto("/reconciliation");
  await page
    .getByRole("button", { name: "Run reconciliation", exact: true })
    .click();
  await page.getByLabel("Search investigations").fill(payment.id);
  const row = page
    .getByRole("row")
    .filter({ has: page.getByText(payment.id, { exact: true }) });
  await row.getByRole("button", { name: "View details", exact: true }).click();
  await page
    .getByRole("button", { name: "Request CrewAI investigation", exact: true })
    .click();
  await expect(
    page.getByRole("status").filter({ hasText: "not executed" }),
  ).toBeVisible();
  await page
    .getByLabel("Review note")
    .fill(
      "Verified both isolated fixture source records and exact decimal balance",
    );
  await page
    .getByRole("button", { name: "Approve allocation", exact: true })
    .click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  const invoice = (
    await (await page.request.get("/api/invoices?q=" + invoiceReference)).json()
  ).items[0];
  expect(Number(invoice.outstanding)).toBe(0);
  await page.goto("/invoices/" + invoice.id);
  await expect(page.locator(".page-header .status")).toHaveText("paid");
});

test("all operational pages and customer history load", async ({ page }) => {
  await signIn(page);
  for (const [path, title] of [
    ["/invoices", "Invoices"],
    ["/transactions", "Transactions"],
    ["/investigations", "Investigations"],
    ["/customers", "Customers"],
    ["/agents", "Agent workspace"],
    ["/collections", "Collections"],
    ["/reports", "Reports & analytics"],
    ["/audit", "Audit trail"],
    ["/settings", "Settings"],
  ]) {
    await page.goto(path);
    await expect(
      page.getByRole("heading", { level: 1, name: title, exact: true }),
    ).toBeVisible();
    await expect(page.getByRole("alert")).toHaveCount(0);
  }
  await page.goto("/customers/synthetic-revenueops-c0");
  await expect(
    page.getByRole("heading", { level: 1, name: "Acorn Design" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Account timeline" }),
  ).toBeVisible();
  await expect(page.getByRole("alert")).toHaveCount(0);
});
