import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const db = createClient(SUPABASE_URL, SERVICE_ROLE, { auth: { persistSession: false } });

function response(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store",
    },
  });
}

async function sha256Hex(value: string): Promise<string> {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

Deno.serve(async (req: Request) => {
  if (req.method !== "GET") return response({ ok: false, error: "method_not_allowed" }, 405);

  const url = new URL(req.url);
  const token = url.searchParams.get("token") ?? "";
  const state = url.searchParams.get("state") ?? "success";
  if (!token || !["success", "error", "cancelled"].includes(state)) {
    return response({ ok: false, error: "invalid_callback" }, 400);
  }

  const tokenHash = await sha256Hex(token);
  const { data, error } = await db.rpc("consume_shortcut_callback", {
    p_token_hash: tokenHash,
    p_status: state,
    p_result: url.searchParams.get("result"),
    p_error_message: url.searchParams.get("errorMessage") ?? url.searchParams.get("error"),
  });

  if (error) return response({ ok: false, error: "consume_failed" }, 500);
  const status = data?.ok === true ? 200 : 410;
  return response(data ?? { ok: false, error: "empty_consume_result" }, status);
});
