import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const RAW_BASE =
  "https://raw.githubusercontent.com/collinsomniac/shortcut-optimization/main/public/shortcut-import-compat";
const MANIFEST_URL = `${RAW_BASE}/manifest.json`;

type Fixture = {
  slug: string;
  filename: string;
  bytes: number;
  sha256: string;
  name?: string;
  mode?: string;
  action_count?: number;
};

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store",
    },
  });
}

async function sha256Hex(bytes: Uint8Array): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function safeFilename(value: string): string {
  return value.replace(/[\\/:*?"<>|\r\n]+/g, "_").slice(0, 180);
}

Deno.serve(async (req: Request) => {
  if (req.method !== "GET") {
    return json({ ok: false, error: "method_not_allowed" }, 405);
  }

  const name = new URL(req.url).searchParams.get("name") ?? "";
  if (!name) {
    return json({ ok: false, error: "missing_name" }, 400);
  }

  let manifestResponse: Response;
  try {
    manifestResponse = await fetch(MANIFEST_URL, {
      headers: { "cache-control": "no-cache" },
    });
  } catch (error) {
    return json(
      { ok: false, error: "manifest_fetch_failed", detail: String(error) },
      502,
    );
  }

  if (!manifestResponse.ok) {
    return json(
      {
        ok: false,
        error: "manifest_unavailable",
        status: manifestResponse.status,
      },
      503,
    );
  }

  const manifest = await manifestResponse.json();
  const fixtures = Array.isArray(manifest?.fixtures)
    ? (manifest.fixtures as Fixture[])
    : [];
  const fixture = fixtures.find((item) => item.slug === name);

  if (!fixture) {
    return json(
      {
        ok: false,
        error: "unknown_public_fixture",
        allowed: fixtures.map((item) => item.slug),
      },
      404,
    );
  }

  const artifactURL = `${RAW_BASE}/${encodeURIComponent(fixture.filename)}`;
  const artifactResponse = await fetch(artifactURL, {
    headers: { "cache-control": "no-cache" },
  });

  if (!artifactResponse.ok) {
    return json(
      {
        ok: false,
        error: "artifact_fetch_failed",
        status: artifactResponse.status,
      },
      502,
    );
  }

  const bytes = new Uint8Array(await artifactResponse.arrayBuffer());
  const magic = bytes.length >= 4
    ? String.fromCharCode(...bytes.subarray(0, 4))
    : "";
  if (magic !== "AEA1") {
    return json(
      { ok: false, error: "invalid_artifact_magic", magic, bytes: bytes.length },
      502,
    );
  }

  if (bytes.length !== fixture.bytes) {
    return json(
      {
        ok: false,
        error: "artifact_size_mismatch",
        expected: fixture.bytes,
        actual: bytes.length,
      },
      502,
    );
  }

  const sha256 = await sha256Hex(bytes);
  if (sha256 !== fixture.sha256) {
    return json(
      {
        ok: false,
        error: "artifact_hash_mismatch",
        expected: fixture.sha256,
        actual: sha256,
      },
      502,
    );
  }

  return new Response(bytes, {
    status: 200,
    headers: {
      "content-type": "application/x-apple-shortcut",
      "content-disposition": `attachment; filename="${safeFilename(fixture.filename)}"`,
      "cache-control": "no-store",
      "x-shortcut-sha256": sha256,
      "x-shortcut-fixture": fixture.slug,
      "x-shortcut-build-mode": fixture.mode ?? "external-control",
      "x-shortcut-action-count": String(fixture.action_count ?? ""),
    },
  });
});
