export default function Home() {
  return (
    <main className="min-h-screen bg-white text-black px-6 py-20">
      <div className="max-w-5xl mx-auto">
        <p className="text-sm uppercase tracking-[0.2em] text-gray-500 mb-6">
          Visakh Sankar
        </p>

        <h1 className="text-5xl md:text-7xl font-semibold leading-tight max-w-4xl">
          Enterprise AI Architect building practical AI systems, simulations, and decision tools.
        </h1>

        <p className="mt-8 text-xl text-gray-600 max-w-3xl leading-8">
          I build working AI demos, architecture simulators, and enterprise focused experiments that explain how modern AI systems actually work.
        </p>

        <div className="mt-12 flex flex-wrap gap-4">
          <a
            href="#builds"
            className="px-6 py-3 bg-black text-white rounded-full"
          >
            View Builds
          </a>
          <a
            href="https://www.linkedin.com/in/YOUR_LINKEDIN_HERE"
            target="_blank"
            rel="noreferrer"
            className="px-6 py-3 border border-black rounded-full"
          >
            LinkedIn
          </a>
        </div>

        <section id="builds" className="mt-24">
          <h2 className="text-3xl font-semibold mb-8">Featured Builds</h2>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="border rounded-2xl p-6">
              <h3 className="text-xl font-semibold">RAG Visual Simulator</h3>
              <p className="mt-3 text-gray-600">
                A visual demo showing chunking, retrieval, and answer generation in a RAG pipeline.
              </p>
              <p className="mt-4 text-sm text-gray-500">Coming soon</p>
            </div>

            <div className="border rounded-2xl p-6">
              <h3 className="text-xl font-semibold">AI Architecture Simulator</h3>
              <p className="mt-3 text-gray-600">
                An interactive tool that recommends AI architecture patterns based on enterprise needs.
              </p>
              <p className="mt-4 text-sm text-gray-500">Coming soon</p>
            </div>

            <div className="border rounded-2xl p-6">
              <h3 className="text-xl font-semibold">Agent Systems Playground</h3>
              <p className="mt-3 text-gray-600">
                A demo that explains how agent orchestration, tools, and workflow execution fit together.
              </p>
              <p className="mt-4 text-sm text-gray-500">Coming soon</p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}