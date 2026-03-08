export function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-white/10 bg-gradient-to-b from-[#1a0f06] to-bgPrimary">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="inline-flex items-center gap-2 rounded-full border border-saffron/40 bg-saffron/10 px-4 py-1 text-xs uppercase tracking-wider text-saffron">
          Rishikesh Travel Network
        </div>
        <h1 className="mt-6 text-4xl font-extrabold leading-tight md:text-6xl">
          Travel Safe. <span className="text-saffron">Connect Real.</span>
        </h1>
        <p className="mt-5 max-w-2xl text-sm text-white/70 md:text-base">
          SafeWander Next is the first migration step to a modern frontend stack while preserving your existing design DNA.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <button className="rounded-md bg-saffron px-5 py-2 text-sm font-bold text-[#1A0F00]">Join as Traveler</button>
          <button className="rounded-md border border-white/20 px-5 py-2 text-sm font-semibold text-white/80">How It Works</button>
        </div>
      </div>
    </section>
  );
}
