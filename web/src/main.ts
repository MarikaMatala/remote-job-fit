// CODE MAP / COMMENTING GUIDE
// File purpose: TypeScript dashboard entry point: initializes the interface and handles Python API events.
// Structure: imports and DOM references -> data types -> safe-output helpers -> job rendering -> API loading -> event handlers.
// Editing tip: if you change an element selector here, update the matching id in web/index.html as well.
// Keep API credentials and personal profile data in the Python backend, never in browser code.

// WORK IN PROGRESS: this browser dashboard is experimental.
// Do not add personal profile data, API keys, access tokens, SMTP credentials,
// private API endpoints, or account details to frontend files. Browser code is
// delivered to users and must be treated as public. Keep secrets in the Python
// backend environment and expose only the minimum data required by the UI.
import "./style.css";

// SECTION 1 START: shape of a job record returned by the Python API.
type Job = {
  id: number;
  title: string;
  company: string;
  source: string;
  location: string;
  url: string;
  published_at: string | null;
  deadline: string | null;
  first_seen_at: string;
  score: number | null;
  analysis: {
    matched_skills?: Array<{ skill: string; keywords: string[] }>;
    missing_skills?: string[];
  };
};

const apiStatus = document.querySelector<HTMLSpanElement>("#api-status")!;
const scanStatus = document.querySelector<HTMLSpanElement>("#scan-status")!;
const scanButton = document.querySelector<HTMLButtonElement>("#scan-button")!;
const jobList = document.querySelector<HTMLDivElement>("#job-list")!;
const jobCount = document.querySelector<HTMLSpanElement>("#job-count")!;

// SECTION 2 START: safe text and URL helpers used when rendering external data.
// FUNCTION SECTION START: escapeHtml.
function escapeHtml(value: unknown): string {
  const entities: Record<string, string> = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  };
  return String(value ?? "").replace(/[&<>"']/g, (character) => entities[character] ?? character);
}

// FUNCTION SECTION START: safeExternalUrl.
// FUNCTION SECTION END: escapeHtml. The next section starts at the next function or at the end of the file.
function safeExternalUrl(value: unknown): string {
  try {
    const parsed = new URL(String(value ?? ""));
    return parsed.protocol === "https:" || parsed.protocol === "http:" ? parsed.href : "#";
  } catch {
    return "#";
  }
}

// SECTION 3 START: build and update the visible job listing cards.
// FUNCTION SECTION START: renderJobs.
// FUNCTION SECTION END: safeExternalUrl. The next section starts at the next function or at the end of the file.
function renderJobs(jobs: Job[]): void {
  jobCount.textContent = `${jobs.length} ${jobs.length === 1 ? "job" : "jobs"}`;
  if (!jobs.length) {
    jobList.innerHTML = '<p class="empty-state">No saved listings yet. Run a scan to collect jobs.</p>';
    return;
  }

  jobList.innerHTML = jobs.map((job) => {
    const matched = (job.analysis?.matched_skills ?? [])
      .map((item) => escapeHtml(item.skill)).join(", ");
    const score = job.score === null ? "N/A" : `${Number(job.score).toFixed(1)}/10`;
    return `
      <article class="job-card">
        <div class="job-main">
          <div class="job-title-row">
            <h3>${escapeHtml(job.title || "Untitled role")}</h3>
            <span class="score">${score}</span>
          </div>
          <p class="company">${escapeHtml(job.company || "Company not listed")}</p>
          <p class="source">Source: ${escapeHtml(job.source || "Unknown source")}</p>
          <p class="location">${escapeHtml(job.location || "Location not specified")}</p>
          <p class="matched">${matched ? `Matched skills: ${matched}` : "No matching skills recorded"}</p>
          <a href="${escapeHtml(safeExternalUrl(job.url))}" target="_blank" rel="noopener noreferrer">View original listing ↗</a>
        </div>
      </article>`;
  }).join("");
}

// SECTION 4 START: retrieve jobs from the local Python API and update the dashboard status.
// FUNCTION SECTION START: loadJobs.
// FUNCTION SECTION END: renderJobs. The next section starts at the next function or at the end of the file.
async function loadJobs(): Promise<void> {
  try {
    const response = await fetch("/api/jobs");
    if (!response.ok) throw new Error(await response.text());
    const payload = await response.json() as { jobs: Job[]; count: number };
    renderJobs(payload.jobs);
    apiStatus.textContent = "Local API connected";
    apiStatus.classList.add("online");
  } catch {
    apiStatus.textContent = "Local API unavailable";
    apiStatus.classList.remove("online");
    jobList.innerHTML = '<p class="empty-state">Start the Python API, then refresh this page. See the README for setup instructions.</p>';
  }
}

// SECTION 5 START: user-triggered scan action and page initialization.
scanButton.addEventListener("click", async () => {
  scanButton.disabled = true;
  scanStatus.textContent = "Scanning public job sources…";
  try {
    const response = await fetch("/api/scan", { method: "POST" });
    const payload = await response.json() as {
      fetched: number; accepted: number; saved: number;
      warnings?: string[];
      source_notices?: Array<{ source: string; legal: string; last_updated?: string | null }>;
      detail?: string;
    };
    if (!response.ok) throw new Error(payload.detail ?? "Scan failed.");
    scanStatus.textContent = `Fetched ${payload.fetched}; ${payload.accepted} matched the worldwide filter; ${payload.saved} new listings saved.`;
    if (payload.warnings?.length) {
      scanStatus.textContent += ` Source warnings: ${payload.warnings.join(" | ")}`;
    }
    for (const notice of payload.source_notices ?? []) {
      const updated = notice.last_updated ? ` (updated ${notice.last_updated})` : "";
      scanStatus.textContent += ` ${notice.source} API notice${updated}: ${notice.legal}`;
    }
    await loadJobs();
  } catch (error) {
    scanStatus.textContent = error instanceof Error ? error.message : "Scan failed.";
  } finally {
    scanButton.disabled = false;
  }
});

void loadJobs();

// FUNCTION SECTION END: loadJobs. The next section starts at the next function or at the end of the file.