const MCP_PLAYGROUND_URL = "https://visakh-ai-lab-bwvwczzzbt9kzykyneu6ev.streamlit.app/";
const RAG_SIMULATOR_URL = "https://visakh-ai-lab-mgbbdk4k9rk8gmkk4ey4tp.streamlit.app/";
const AI_ARCH_SIMULATOR_URL = "https://visakh-ai-lab-nzsdsdjsm45vyayjpvgfmk.streamlit.app/";
const AGENT_PLAYGROUND_URL = "https://visakh-ai-lab-dnyxly82duv6rrxvvs9r9m.streamlit.app/";

interface Build {
  title: string;
  description: string;
  tags: string[];
  href?: string;
  live: boolean;
  isNew?: boolean;
}

const BUILDS: Build[] = [
  {
    title: "MCP Playground",
    description:
      "Watch AI connect to the world in real time via Model Context Protocol. Every JSON-RPC 2.0 message exposed — handshake, tool discovery, execution loop. 5 live tools including web search, calculator, weather, and database queries.",
    tags: ["MCP", "Agents", "JSON-RPC", "OpenAI", "Streamlit"],
    href: MCP_PLAYGROUND_URL || undefined,
    live: !!MCP_PLAYGROUND_URL,
    isNew: true,
  },
  {
    title: "RAG Visual Simulator",
    description:
      "Upload any document and watch chunking, embedding, retrieval, and answer generation happen in real time. Makes RAG pipelines legible.",
    tags: ["RAG", "OpenAI", "FAISS", "Streamlit"],
    href: RAG_SIMULATOR_URL,
    live: true,
  },
  {
    title: "AI Architecture Simulator",
    description:
      "Describe your enterprise use case and get an expert architecture recommendation with live reasoning, trade-off analysis, and an architecture brief.",
    tags: ["Architecture", "LLM", "Decision Tools", "Streamlit"],
    href: AI_ARCH_SIMULATOR_URL,
    live: true,
  },
  {
    title: "Agent Systems Playground",
    description:
      "Watch an AI agent think, choose tools, and reason its way to an answer — every step exposed. Includes multi-agent orchestration with Research, Analysis, and Writer agents.",
    tags: ["Agents", "Orchestration", "OpenAI", "Streamlit"],
    href: AGENT_PLAYGROUND_URL,
    live: true,
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-white text-black px-6 py-20">
      <div className="max-w-5xl mx-auto">
        <p className="text-sm uppercase tracking-[0.2em] text-gray-500 mb-6">
          Visakh Sankar
        </p>

        <h1 className="text-5xl md:text-7xl font-semibold leading-tight max-w-4xl">
          Enterprise AI Architect building practical AI systems, simulations,
          and decision tools.
        </h1>

        <p className="mt-8 text-xl text-gray-600 max-w-3xl leading-8">
          I build working AI demos, architecture simulators, and
          enterprise-focused experiments that explain how modern AI systems
          actually work.
        </p>

        <div className="mt-12 flex flex-wrap gap-4">
          <a
            href="#builds"
            className="px-6 py-3 bg-black text-white rounded-full hover:bg-gray-800 transition-colors"
          >
            View Builds
          </a>
          <a
            href="https://www.linkedin.com/in/visakhsankar/"
            target="_blank"
            rel="noreferrer"
            className="px-6 py-3 border border-black rounded-full hover:bg-gray-50 transition-colors"
          >
            LinkedIn
          </a>
        </div>

        <section id="builds" className="mt-24">
          <h2 className="text-3xl font-semibold mb-2">Featured Builds</h2>
          <p className="text-gray-500 mb-10">Working demos, not slide decks.</p>

          <div className="grid md:grid-cols-3 gap-6">
            {BUILDS.map((build) => (
              <div
                key={build.title}
                className="border rounded-2xl p-6 flex flex-col justify-between hover:shadow-md transition-shadow"
              >
                <div>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="text-xl font-semibold leading-snug">
                        {build.title}
                      </h3>
                      {build.isNew && (
                        <span className="shrink-0 inline-flex items-center text-xs font-bold text-white bg-black rounded-full px-2.5 py-0.5 tracking-wide">
                          New
                        </span>
                      )}
                    </div>
                    {build.live ? (
                      <span className="ml-3 mt-1 shrink-0 inline-flex items-center gap-1 text-xs font-medium text-green-700 bg-green-50 border border-green-200 rounded-full px-2 py-0.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                        Live
                      </span>
                    ) : (
                      <span className="ml-3 mt-1 shrink-0 text-xs text-gray-400">
                        Soon
                      </span>
                    )}
                  </div>

                  <p className="text-gray-600 text-sm leading-relaxed">
                    {build.description}
                  </p>

                  <div className="mt-4 flex flex-wrap gap-2">
                    {build.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-xs bg-gray-100 text-gray-600 rounded-full px-2.5 py-1"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-6">
                  {build.href ? (
                    <a
                      href={build.href}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sm font-medium text-black underline underline-offset-4 hover:text-gray-500 transition-colors"
                    >
                      Open demo →
                    </a>
                  ) : (
                    <p className="text-sm text-gray-400">In progress</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
