const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(response.ok ? "Invalid JSON response" : `Request failed (${response.status})`);
  }

  if (!response.ok) {
    const detail = data.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d) => d.msg || JSON.stringify(d)).join("; ")
          : data.message || "Request failed";
    throw new Error(message);
  }
  return data;
}

function show(data) {
  $("snapshot").textContent = JSON.stringify(data, null, 2);
  $("page-meta").textContent = `${data.title || ""} — ${data.url || ""}`;
  const img = $("screenshot");
  img.src = "/api/screenshot?t=" + Date.now();
  img.style.display = "block";
}

async function refresh() {
  try {
    show(await api("/api/snapshot"));
  } catch (e) {
    $("snapshot").textContent = e.message;
  }
}

$("open").onclick = async () => {
  try {
    show(
      await api("/api/open", {
        method: "POST",
        body: JSON.stringify({ url: $("url").value }),
      })
    );
  } catch (e) {
    $("snapshot").textContent = e.message;
  }
};

$("inspect").onclick = refresh;
$("refresh").onclick = refresh;

$("click").onclick = async () => {
  try {
    show(
      await api("/api/click", {
        method: "POST",
        body: JSON.stringify({ selector: $("selector").value }),
      })
    );
  } catch (e) {
    $("snapshot").textContent = e.message;
  }
};

$("fill").onclick = async () => {
  try {
    show(
      await api("/api/fill", {
        method: "POST",
        body: JSON.stringify({
          selector: $("selector").value,
          value: $("value").value,
        }),
      })
    );
  } catch (e) {
    $("snapshot").textContent = e.message;
  }
};

$("ask").onclick = async () => {
  try {
    const data = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({ prompt: $("prompt").value }),
    });
    $("answer").textContent = data.response;
  } catch (e) {
    $("answer").textContent = e.message;
  }
};

$("run-agent").onclick = async () => {
  const button = $("run-agent");
  button.disabled = true;
  $("agent-result").textContent = "Running agent…";
  try {
    const data = await api("/api/agent", {
      method: "POST",
      body: JSON.stringify({ goal: $("goal").value }),
    });
    $("agent-result").textContent = JSON.stringify(data, null, 2);
    if (data.results?.length) {
      const last = data.results[data.results.length - 1].result;
      if (last) show(last);
    }
  } catch (e) {
    $("agent-result").textContent = e.message;
  } finally {
    button.disabled = false;
  }
};

(async () => {
  try {
    const data = await api("/api/health");
    $("health").textContent = "● Online";
    $("health").title =
      data.mcp_endpoint + " • " + data.model + " • vision: " + data.vision_model;
  } catch {
    $("health").textContent = "Offline";
  }
})();
