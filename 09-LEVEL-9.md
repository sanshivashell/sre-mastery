# Stage 9 — Level 9: Distributed Limits

> **The demand:** Scale Checkout until it hits the *hard, proven* limits of distributed systems — and learn to design within them rather than pretend they don't exist.

Checkout has been a modest service. Stage 9 imagines it at global scale, where consensus, consistency, clocks, tail latency, and coordination cost stop being abstractions and start dictating your architecture. This is the level of proven impossibility results — you don't beat them, you respect them.

---

## Prerequisites (from Stages 1–8)
- A fully reliable Checkout with real capacity data and load-test history
- The "never oversell" inventory invariant (from Stage 1) — now the crux

## Tasks — one per L9 module (anchored in each module's lab)

1. **Consensus & coordination** *(L9-M01 — Lab: Reason About a Consensus Cluster).* Checkout's inventory now needs distributed agreement to never oversell. Reason about a consensus cluster (Raft/etcd-style) behind it: quorum, leader, what happens under partition. Where is coordination unavoidable?
2. **Consistency models** *(L9-M02 — Lab: Place a Workload on the Spectrum).* Map each Checkout operation onto the consistency spectrum: payment must be linearizable, a like-count can be eventual, the user's own cart wants read-your-writes. Choose the *weakest sufficient* model per operation.
3. **Time, clocks & ordering** *(L9-M03 — Lab: Build the Clocks, See the Order).* Show why you can't trust wall-clock time to order events across Checkout's nodes; use logical/hybrid clocks to establish a defensible order for, say, cart mutations.
4. **Queueing & tail latency** *(L9-M04 — Lab: See the Curve, Tame the Tail).* Analyze Checkout's tail latency under load (the 1/(1-ρ) curve from Stage 3/5), find where the tail explodes, and apply a technique (hedging, concurrency limits) to tame it.
5. **Capacity modeling** *(L9-M05 — Lab: Model the Scaling Curve).* Fit the Universal Scalability Law to Checkout's load-test data (from Stage 3), extract contention (α) and coherency (β), and find the scaling **knee** — the node count past which adding nodes hurts.
6. **Distributed-systems judgment** *(L9-M06 — Lab: The Judgement Portfolio).* Produce a trade-off table for Checkout: for each operation, its invariant, chosen consistency model, CAP/PACELC stance, and the coordination cost you're paying. This is the synthesis of the level.

## The integration twist
Every choice here must **preserve the invariants and SLOs from earlier stages**. Choosing eventual consistency for inventory to scale further would violate "never oversell" (Stage 1) — so you must find the *weakest* model that still holds the invariant, and pay the coordination cost knowingly. The USL knee (task 5) becomes the hard ceiling your Stage-5 capacity plan must respect. Level 9 is where you learn that some reliability problems are *coordination* problems, bounded by proof.

## Deliverables
- A reasoned design for consensus behind the inventory invariant
- A per-operation consistency map (the spectrum placement)
- A logical/hybrid-clock ordering demonstration
- A tail-latency analysis + one tail-taming technique applied
- A USL fit of Checkout's data with the knee identified
- The distributed-systems trade-off portfolio (the L9 capstone artifact)

## Definition of done
- [ ] "Never oversell" holds under partition, with the coordination cost named
- [ ] Each operation is on its weakest-sufficient consistency model, justified
- [ ] You can show why wall-clock ordering fails and logical clocks fix it
- [ ] Tail latency analyzed and improved with evidence
- [ ] USL fitted; the scaling knee is a real number
- [ ] A defensible trade-off table covers every Checkout operation

## Assessment rubric
| Level | Looks like |
|-------|-----------|
| Novice | Recites CAP; picks consistency by habit; no coordination cost named |
| Competent | Weakest-sufficient per operation; USL fitted; tail tamed with evidence |
| Mastery | Every guarantee is priced in latency/availability/scale; the invariant survives partition at known cost; the trade-off portfolio would guide a real architecture decision |
