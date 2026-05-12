Computational Seismology (GLY 6739)

Research-Level Homework Sequence

Robust RSAM Processing of Real Observatory Data

University of South Florida
Spring 2026

⸻

Instructor’s Note

These assignments are intentionally designed to resemble real observatory and research workflows rather than simplified classroom exercises.

You will work with:

* large continuous waveform archives,
* imperfect instrumentation,
* corrupted telemetry,
* damaged sensors,
* operational processing pipelines,
* and computational workflows that may fail unexpectedly.

This means there may not always be a single “correct” answer.

That is normal.

The purpose of these assignments is to help you develop:

* scientific judgment,
* operational instincts,
* robust computational workflows,
* and experience working with messy real-world seismic data.

These assignments are closer to research and observatory operations than traditional homework.

⸻

⸻

Overview

This homework sequence focuses on:

* continuous seismic data,
* RSAM (Real-time Seismic Amplitude Measurement),
* robust preprocessing,
* and scalable observatory workflows.

The assignments are divided into two linked stages:

Homework	Focus
Week 10	Exploratory local processing and preprocessing strategies
Week 12	Scalable server-side operational workflows on newton

Together, these assignments form a miniature research project in computational seismology.

⸻

Why We Are Doing This

In volcano observatories, earthquake monitoring systems, environmental seismology, and rocket seismology, data are often messy and imperfect.

Operational scientists must learn how to:

* diagnose data problems,
* identify instrumentation artifacts,
* build robust processing workflows,
* avoid misleading results,
* and process very large datasets efficiently.

You are not simply learning how to compute RSAM.

You are learning how to think like an observatory scientist.

⸻

What Is RSAM?

RSAM (Real-time Seismic Amplitude Measurement) is a compressed representation of continuous seismic amplitude over time.

Instead of storing or plotting every waveform sample, we compute:

* average amplitude,
* median amplitude,
* reduced displacement,
* or related metrics

over fixed time windows (e.g., 1 minute).

RSAM is widely used in:

* volcano monitoring,
* eruption detection,
* tremor tracking,
* lahar monitoring,
* and operational seismic surveillance.

However:

RSAM is extremely sensitive to preprocessing choices and data quality.

This assignment explores those issues directly.

⸻

Homework Structure

Week 10 Homework

Exploratory Local Processing

In Week 10, you will:

* select one of several continuous seismic datasets,
* compute RSAM products locally,
* explore preprocessing strategies,
* investigate how different forms of data corruption affect RSAM,
* and document what works and what fails.

This homework is exploratory and research-oriented.

You are encouraged to:

* experiment,
* compare approaches,
* diagnose failures,
* and discuss problems with the instructor.

The goal is not to produce a perfect RSAM product.

The goal is to discover:

* how fragile continuous seismic processing can be,
* and how operational workflows evolve in practice.

⸻

Week 12 Homework

Scalable Operational Workflow on Newton

In Week 12, you will:

* adapt your workflow to run on the newton server,
* process data incrementally,
* avoid unnecessary copying of waveform archives,
* and build a more operationally realistic processing pipeline.

This stage emphasizes:

* scalability,
* computational efficiency,
* incremental processing,
* and efficient archive usage.

You will learn that:

* large observatory datasets cannot be processed like small laptop datasets,
* computation should move to the data,
* and operational robustness matters as much as scientific correctness.

⸻

Datasets

You may work with one or more of the following datasets.

Dataset	Characteristics
Sakurajima SDS archive	Relatively clean volcanic seismic data
Nevado del Ruiz SDS_GCF	More problematic telemetry and instrument artifacts
KSC 2026 rocket-seismology archive	Large heterogeneous deployment with changing station availability
Other instructor-approved datasets	Depending on course development

Each dataset presents different challenges.

Part of the assignment is learning how dataset characteristics affect workflow design.

⸻

What You Will Discover

Lesson 1 — Real Seismic Data Are Messy

You will encounter:

* spikes,
* telemetry dropouts,
* missing data,
* baseline shifts,
* strange ramps,
* timing irregularities,
* and nonphysical artifacts.

Simple textbook workflows often fail on these datasets.

This is normal in real observatory operations.

⸻

Lesson 2 — Preprocessing Order Matters

You will likely discover that:

* filtering before merging can create severe artifacts,
* tapering matters,
* detrending alone is often insufficient,
* clipping can help but may also suppress real signals,
* and edge effects can contaminate RSAM products.

The order of operations matters enormously.

⸻

Lesson 3 — There Is No Perfect Solution

One of the most important lessons is:

Even experienced researchers do not always know the optimal preprocessing strategy.

Operational seismic processing often involves:

* tradeoffs,
* experimentation,
* empirical testing,
* and scientific judgment.

You are expected to engage with that uncertainty.

⸻

Lesson 4 — Large Datasets Change Everything

Students consistently discover that:

* waveform archives are huge,
* memory usage becomes a serious issue,
* processing time matters,
* and inefficient workflows quickly become impractical.

This is why:

* incremental processing,
* one-day-at-a-time workflows,
* and compressed products like RSAM exist.

⸻

Lesson 5 — Operational Workflows Matter

You will learn:

* why SDS archives exist,
* why server-side processing is important,
* why copying entire waveform archives is inefficient,
* and how observatories structure continuous seismic processing.

This is real computational seismology infrastructure.

⸻

Suggested Workflow

The following workflow generally works well:

1. Read one UTC day at a time.
2. Add extra time padding before and after the target day.
3. Merge traces carefully.
4. Remove obvious spikes or pathological amplitudes.
5. Detrend and taper.
6. Apply conservative filtering.
7. Trim back to the target day.
8. Compute RSAM.
9. Save RSAM products incrementally.
10. Read RSAM back for plotting and analysis.

However:

* you are encouraged to explore alternatives,
* especially if your dataset contains severe artifacts.

⸻

Recommended Processing Ideas

You may experiment with:

* percentile clipping,
* median filtering,
* robust statistics,
* gap-aware processing,
* baseline stabilization,
* high-pass filtering,
* step/ramp removal,
* and selective channel usage (e.g., vertical-only).

Not all approaches will work equally well.

Part of the assignment is evaluating their strengths and weaknesses.

⸻

Expected Difficulties

You will likely encounter:

* failed processing runs,
* corrupted traces,
* memory issues,
* unexpectedly large runtime,
* filter instability,
* and datasets that behave differently than expected.

This is normal.

You are encouraged to:

* work incrementally,
* test on small subsets first,
* save intermediate products,
* and keep careful notes.

⸻

What We Are Evaluating

This is not a traditional “right answer” homework.

You will be evaluated primarily on:

* engagement,
* scientific reasoning,
* persistence,
* workflow design,
* thoughtful experimentation,
* and operational thinking.

We are not expecting:

* perfect preprocessing,
* perfectly clean RSAM,
* or flawless operational pipelines.

Instead, we want to see:

* how you diagnose problems,
* how you adapt,
* and how you think scientifically about difficult data.

⸻

Collaboration and Help

You are encouraged to:

* ask questions,
* discuss ideas,
* compare approaches,
* and seek help from the instructor.

In real observatory operations:

* collaborative debugging and workflow refinement are normal and essential.

Seeking help is a sign of engagement, not weakness.

⸻

Important Operational Insight

One of the major lessons from previous years is:

Computation should usually move to the data, not the other way around.

For large observatory datasets:

* copying waveform archives is slow,
* memory usage becomes prohibitive,
* and local workflows become inefficient.

Efficient operational systems:

* process incrementally,
* read directly from shared archives,
* and generate compressed products such as RSAM.

⸻

Lessons Learned From Previous Students

Previous students discovered that:

* processing very large waveform streams can exhaust memory,
* one-day-at-a-time processing is far more stable,
* clipping helps with spikes but may not solve baseline drift,
* damaged instruments can produce very strange low-frequency artifacts,
* some channels may fail unpredictably,
* and robust workflows evolve through experimentation.

Several students also discovered that:

* there is often no single “correct” preprocessing pipeline,
* and even instructors continue refining these workflows.

That is normal in research-level computational seismology.

⸻

Final Thought

This assignment sequence is intentionally close to real research and operational seismology.

You will likely experience:

* confusion,
* failed processing runs,
* unexpected artifacts,
* and incomplete solutions.

That is normal.

In fact, that is the point.

The most important outcome is not:

“I computed RSAM.”

The most important outcome is:

“I learned how difficult real-world seismic data processing actually is, and how to think critically about it.”