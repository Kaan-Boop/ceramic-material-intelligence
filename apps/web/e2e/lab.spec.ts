import { test, expect } from "@playwright/test";

let runtimeErrors: string[] = [];

test.beforeEach(async ({ page }) => {
  runtimeErrors = [];
  page.on("pageerror", (e) => runtimeErrors.push(e.message));
  await page.goto("/");
  await expect(page.getByLabel("Miktar 1", { exact: true })).toBeVisible();
});

test.afterEach(async ({ page }) => {
  expect(runtimeErrors).toEqual([]);
  await expect(page.locator("[data-nextjs-dialog]")).toHaveCount(0);
});

test("real analysis, stale guard, comparison and export", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.getByRole("button", { name: "Reçeteyi analiz et" }).click();
  await expect(page.getByText("Oksitler & UMF")).toBeVisible();
  await expect(page.getByText("90,61", { exact: false }).first()).toBeVisible();
  await page
    .getByRole("button", { name: "Karşılaştırma için sabitle" })
    .click();
  await page.getByLabel("Miktar 1", { exact: true }).fill("45,5");
  await expect(
    page.getByText("Girdi değişti.", { exact: false }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "JSON raporu indir" }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Reçeteyi analiz et" }).click();
  await expect(page.getByText("Girdi değişti.", { exact: false })).toHaveCount(
    0,
  );
  await expect(
    page.getByText("Kimyasal karşılaştırma", { exact: true }),
  ).toBeVisible();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "JSON raporu indir" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/^ceramic-report-.*\.json$/);
  const stream = await download.createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of stream!) chunks.push(Buffer.from(chunk));
  const report = JSON.parse(Buffer.concat(chunks).toString());
  expect(report.request.ingredients[0].amount).toBe(45.5);
  expect(report.chemistry.evidence_kind).toBe("CALCULATED");
  expect(report.chemistry.predictions.status).toBe("UNAVAILABLE");
  expect(errors).toEqual([]);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: `test-results/report-${test.info().project.name}.png`,
    fullPage: true,
  });
});

test("validation, pure silica undefined ratios, local draft", async ({
  page,
}) => {
  for (let i = 1; i <= 4; i++)
    await page.getByLabel(`Miktar ${i}`, { exact: true }).fill("0");
  await page.getByRole("button", { name: "Reçeteyi analiz et" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText(
    "Baz reçetenin toplamı sıfır olamaz",
  );
  await page.getByLabel("Miktar 2", { exact: true }).fill("100");
  await page.getByRole("button", { name: "Reçeteyi analiz et" }).click();
  await expect(
    page.getByText("UMF hesaplanamıyor:", { exact: false }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Taslağı kaydet" }).click();
  await page.reload();
  await expect(page.getByLabel("Miktar 1", { exact: true })).toHaveValue("40");
  await page.getByRole("button", { name: "Taslağı aç" }).click();
  await expect(page.getByLabel("Miktar 1", { exact: true })).toHaveValue("0");
  await expect(page.getByLabel("Miktar 2", { exact: true })).toHaveValue("100");
});

test("materials, scope labels and routes", async ({ page }) => {
  await page.getByRole("button", { name: "Malzeme kütüphanesi" }).click();
  await expect(page.getByRole("heading", { name: "Saf kalsit" })).toBeVisible();
  await page.getByRole("button", { name: "Model sınırları" }).click();
  await expect(
    page.getByText("Kalibre model henüz yok.", { exact: false }),
  ).toBeVisible();
  await page.goto("/analyze");
  await expect(
    page.getByRole("button", { name: "Reçeteyi analiz et" }),
  ).toBeVisible();
});

test("network failure keeps prior report marked stale", async ({ page }) => {
  await page.getByRole("button", { name: "Reçeteyi analiz et" }).click();
  await expect(page.getByText("Oksitler & UMF")).toBeVisible();
  await page.getByLabel("Miktar 1", { exact: true }).fill("41");
  await page.route("**/api/v1/analyses", (r) =>
    r.fulfill({ status: 503, body: "Unavailable" }),
  );
  await page.getByRole("button", { name: "Reçeteyi analiz et" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toBeVisible();
  await expect(
    page.getByText("Girdi değişti.", { exact: false }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "JSON raporu indir" }),
  ).toBeDisabled();
});

test("late response cannot replace edited draft result", async ({ page }) => {
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/v1/analyses", async (route) => {
    await gate;
    await route.continue();
  });
  await page.getByRole("button", { name: "Reçeteyi analiz et" }).click();
  await expect(
    page.getByRole("button", { name: "Hesaplanıyor" }),
  ).toBeVisible();
  await page.getByLabel("Miktar 1", { exact: true }).fill("49");
  const responded = page.waitForResponse("**/api/v1/analyses");
  release();
  await responded;
  await expect(page.getByText("Oksitler & UMF")).toHaveCount(0);
  await expect(page.getByLabel("Miktar 1", { exact: true })).toHaveValue("49");
});

test("addition stays outside the normalized base", async ({ page }) => {
  await page.getByRole("button", { name: "Malzeme ekle" }).click();
  await page
    .getByLabel("Malzeme 5", { exact: true })
    .selectOption("pure_silica");
  await page.getByLabel("Rol 5", { exact: true }).selectOption("ADDITION");
  await page.getByLabel("Miktar 5", { exact: true }).fill("2");
  await page.getByRole("button", { name: "Reçeteyi analiz et" }).click();
  await expect(page.getByText("102 g TOPLAM", { exact: true })).toBeVisible();
});

test('sourced body range and honest outcome report', async ({ page }) => {
  await page.getByText('Bünye · isteğe bağlı kaynaklı aralık', { exact: true }).click();
  await page.getByLabel('Bünye · Ürün / analiz sürümü', { exact: true }).fill('Synthetic test body');
  await page.getByLabel('Bünye · Alt sınır · °C', { exact: true }).fill('1200');
  await page.getByLabel('Bünye · Üst sınır · °C', { exact: true }).fill('1280');
  await page.getByLabel('Bünye · Kaynak URL / belge referansı', { exact: true }).fill('synthetic-test-only');
  await page.getByLabel('Bünye · Atmosfer, hız ve diğer kaynak koşulları', { exact: true }).fill('Fixture only, not a commercial recommendation');
  await page.getByLabel('Hedef sıcaklık · °C', { exact: true }).fill('1230');
  await page.getByRole('button', { name: 'Reçeteyi analiz et' }).click();
  const process = page.getByRole('region', { name: 'Çamur sır pişirim değerlendirmesi' });
  await expect(process).toContainText('Bildirilen aralık içinde; uyumluluk garantisi değil.');
  await expect(process.locator('summary').filter({ hasText: 'Tahmin mevcut değil' })).toHaveCount(6);
  await process.getByText('Soğuma sonrası sır–bünye uyumu · Tahmin mevcut değil', { exact: true }).click();
  await expect(process).toContainText('Uyumlu koşullarda ölçülmüş genleşme eğrileri');
  await page.getByRole('button', { name: 'Taslağı kaydet' }).click();
  await page.reload();
  await page.getByRole('button', { name: 'Taslağı aç' }).click();
  await page.getByText('Bünye · isteğe bağlı kaynaklı aralık', { exact: true }).click();
  await expect(page.getByLabel('Bünye · Alt sınır · °C', { exact: true })).toHaveValue('1200');
  await page.getByLabel('Hedef sıcaklık · °C', { exact: true }).fill('1300');
  await page.getByRole('button', { name: 'Reçeteyi analiz et' }).click();
  await expect(process).toContainText('Bildirilen aralığın üzerinde.');
});
